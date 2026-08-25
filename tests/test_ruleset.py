import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from clipfix import apply_rules, initialize_rules_file, load_rules, rules_path


class ConfluenceRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules("ruleset.example.yaml")

    def test_confluence_link_without_anchor(self):
        source = (
            "https://confluence.example.com/spaces/Example/pages/"
            "772928068/Using+AI+for+coding+related+activities"
        )

        self.assertEqual(
            apply_rules(source, self.rules),
            "https://confluence.example.com/pages/"
            "releaseview.action?pageId=772928068",
        )

    def test_confluence_link_keeps_internal_anchor(self):
        source = (
            "https://confluence.example.com/spaces/Example/pages/"
            "772928068/Using+AI+for+coding+related+activities"
            "#UsingAIforcodingrelatedactivities-PrimaryTargetedAudience"
        )

        self.assertEqual(
            apply_rules(source, self.rules),
            "https://confluence.example.com/pages/"
            "releaseview.action?pageId=772928068"
            "#UsingAIforcodingrelatedactivities-PrimaryTargetedAudience",
        )


class RulesPathTests(unittest.TestCase):
    def test_rules_path_defaults_to_home_directory(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("os.path.expanduser", return_value="/home/example"),
        ):
            self.assertEqual(
                rules_path(),
                os.path.join("/home/example", ".clipfix", "ruleset.yaml"),
            )

    def test_rules_path_supports_environment_override(self):
        with patch.dict(os.environ, {"CLIPFIX_RULESET": "~/custom-rules.yaml"}):
            with patch("os.path.expanduser", return_value="/home/example/custom.yaml"):
                self.assertEqual(
                    rules_path(),
                    os.path.abspath("/home/example/custom.yaml"),
                )

    def test_initialize_rules_file_copies_example(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            example_path = directory_path / "ruleset.example.yaml"
            destination_path = directory_path / ".clipfix" / "ruleset.yaml"
            example_path.write_text("rules: []\n", encoding="utf-8")

            initialize_rules_file(destination_path, example_path)

            self.assertEqual(
                destination_path.read_text(encoding="utf-8"),
                "rules: []\n",
            )

    def test_initialize_rules_file_does_not_overwrite_existing_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            example_path = directory_path / "ruleset.example.yaml"
            destination_path = directory_path / ".clipfix" / "ruleset.yaml"
            destination_path.parent.mkdir()
            example_path.write_text("rules: []\n", encoding="utf-8")
            destination_path.write_text("personal rules\n", encoding="utf-8")

            initialize_rules_file(destination_path, example_path)

            self.assertEqual(
                destination_path.read_text(encoding="utf-8"),
                "personal rules\n",
            )


if __name__ == "__main__":
    unittest.main()
