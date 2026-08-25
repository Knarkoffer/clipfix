# Copyright (C) 2026 Knarkoffer
# SPDX-License-Identifier: GPL-3.0-only

import atexit
import logging
import os.path
import re
import shutil
import sys
import threading
import time

import yaml

RULESET_RELOAD_INTERVAL_SECONDS = 5
RULESET_ENVIRONMENT_VARIABLE = "CLIPFIX_RULESET"


def resource_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def rules_path():
    configured_path = os.environ.get(RULESET_ENVIRONMENT_VARIABLE)

    if configured_path:
        return os.path.abspath(os.path.expanduser(configured_path))

    return os.path.join(os.path.expanduser("~"), ".clipfix", "ruleset.yaml")


def initialize_rules_file(path, example_path=None):
    if os.path.exists(path):
        return

    if example_path is None:
        example_path = resource_path("ruleset.example.yaml")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(example_path, "rb") as source, open(path, "xb") as destination:
            shutil.copyfileobj(source, destination)
    except FileExistsError:
        # Another Clipfix process created the file after the existence check.
        pass


def configure_logging(path):
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )


def delete_log_file(path):
    logging.shutdown()

    if os.path.isfile(path):
        os.remove(path)


def load_rules(path=None):
    if path is None:
        path = rules_path()

    if not os.path.isfile(path):
        raise FileNotFoundError("No ruleset found!")

    with open(path, encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    rules = data.get("rules", [])

    if not isinstance(rules, list):
        raise ValueError("Ruleset must contain a list named 'rules'")

    return rules


def load_rules_and_mtime(path):
    rules = load_rules(path)
    rules_mtime = os.path.getmtime(path)
    return rules_mtime, rules


def load_rules_if_changed(path, current_mtime, current_rules):
    try:
        new_mtime = os.path.getmtime(path)

        if new_mtime == current_mtime:
            return current_mtime, current_rules

        new_mtime, new_rules = load_rules_and_mtime(path)
        logging.info("Reloaded ruleset: %s rules", len(new_rules))
        return new_mtime, new_rules

    except Exception as error:
        logging.exception("Could not reload ruleset: %s", error)
        return current_mtime, current_rules


def apply_rules(text, rules):
    for rule in rules:
        if not rule.get("enabled", False):
            continue

        if rule.get("type") != "regex_replace":
            continue

        pattern = rule.get("pattern")
        replacement = rule.get("replacement", "")

        new_text = re.sub(pattern, replacement, text)

        if new_text != text:
            logging.info(
                "Applied rule: %s, converted %s to %s",
                rule.get("name", "Unnamed rule"),
                text,
                new_text,
            )
            text = new_text

            if rule.get("stop_after_processing", False):
                break

    return text


def monitor_clipboard(rules_path, rules_mtime, rules):
    import pyperclip

    previous_text = None
    last_rules_check = 0

    while True:
        try:
            now = time.monotonic()

            if now - last_rules_check >= RULESET_RELOAD_INTERVAL_SECONDS:
                rules_mtime, rules = load_rules_if_changed(
                    rules_path,
                    rules_mtime,
                    rules,
                )
                last_rules_check = now

            current_text = pyperclip.paste()

            if current_text != previous_text:
                fixed_text = apply_rules(current_text, rules)

                if fixed_text != current_text:
                    pyperclip.copy(fixed_text)
                    logging.info("Clipboard updated")

                previous_text = fixed_text

        except Exception as error:
            logging.exception("Clipboard monitor error: %s", error)

        time.sleep(0.25)


def load_icon(path):
    from PIL import Image

    if not os.path.isfile(path):
        sys.exit("No icon found!")

    return Image.open(path)


def on_exit(icon, item, log_path):
    delete_log_file(log_path)
    icon.stop()


def main():
    import pystray

    configured_rules_path = rules_path()
    log_path = resource_path("app.log")

    try:
        delete_log_file(log_path)
        configure_logging(log_path)
        atexit.register(delete_log_file, log_path)
    except Exception as error:
        sys.exit(str(error))

    try:
        initialize_rules_file(configured_rules_path)
        rules_mtime, rules = load_rules_and_mtime(configured_rules_path)
    except Exception as error:
        sys.exit(str(error))

    icon = pystray.Icon(
        "background_app",
        load_icon(resource_path("clipboard_icon.png")),
        "Clipfix",
        menu=pystray.Menu(
            pystray.MenuItem("Exit", lambda icon, item: on_exit(icon, item, log_path)),
        ),
    )

    threading.Thread(
        target=monitor_clipboard,
        args=(configured_rules_path, rules_mtime, rules),
        daemon=True,
    ).start()

    icon.run()


if __name__ == "__main__":
    main()
