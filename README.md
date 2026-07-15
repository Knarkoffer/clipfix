# Clipfix

Clipfix is a small Python tray app that watches the clipboard and rewrites matching text with configurable regex rules. It is meant for quick local cleanup tasks such as removing tracking parameters, extracting IDs from URLs, or normalizing links you copy often.

## Features

- Monitors clipboard text in the background.
- Applies ordered `regex_replace` rules from `ruleset.yaml`.
- Reloads the ruleset automatically while running.
- Supports per-rule enable flags and stop-after-match behavior.
- Provides a tray icon with an Exit menu item.

## Requirements

- Python 3
- Python packages:
  - `pyperclip`
  - `pystray`
  - `pyyaml`
  - `pillow`

Install the packages with:

```bash
python -m pip install -e .
```


On Windows, `py` can be used instead:

```bat
py -m pip install -e .
```

## Usage

Run the app from the repository directory:

```bash
clipfix
```

On Windows, `run_clipfix.bat` is included only as an ease-of-use launcher. It starts `clipfix.py` with `pyw` or `pythonw` when available so the app can run without a console window.

When Clipfix is running, copy text as usual. If the clipboard text matches an enabled rule, Clipfix replaces the clipboard contents with the transformed value.

## Rules

Rules live in `ruleset.yaml` next to `clipfix.py`.

```yaml
rules:
  - name: "Remove ChatGPT UTM source"
    enabled: true
    type: regex_replace
    pattern: '\?utm_source=chatgpt\.com$'
    replacement: ''
    stop_after_processing: false
```

Rule fields:

- `name`: Human-readable rule name used in logs.
- `enabled`: Set to `true` to activate the rule.
- `type`: Currently expected to be `regex_replace`.
- `pattern`: Python regular expression to match clipboard text.
- `replacement`: Replacement string passed to `re.sub`.
- `stop_after_processing`: Stop applying further rules after this rule changes the text.

Rules are applied in file order. Clipfix checks for ruleset changes every few seconds and keeps the previous rules if a reload fails.

## Project Files

- `clipfix.py`: Main tray application and clipboard monitor.
- `ruleset.yaml`: Editable regex rules.
- `clipboard_icon.png`: Tray icon.
- `run_clipfix.bat`: Optional Windows convenience launcher.

## License

MIT License. See `LICENSE`.
