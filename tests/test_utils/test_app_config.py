import os
from pathlib import Path
from unittest import TestCase

from utils.app_config import AppConfig


class TestAppConfig(TestCase):
    """Test cases for application configuration settings."""

    def setUp(self):
        """Set up the test environment."""
        test_config_path = Path(__file__).parent / "test_config.toml"

        self.app_config = AppConfig.from_config(test_config_path)

    def test_load_config(self):
        """Test loading configuration from a TOML file."""
        self.assertIsInstance(self.app_config, AppConfig)
        self.assertEqual(self.app_config.app_setting.app_name, "Job Analyzer")
        self.assertEqual(self.app_config.app_setting.app_author, "Abugh")
        self.assertEqual(
            self.app_config.app_setting.app_log_level.to_string(), "LogLevel.INFO"
        )

    def test_save_config_and_load(self):
        """Test saving configuration to a TOML file."""
        test_config_path = Path(__file__).parent / "test_config_runtime.toml"
        self.app_config.save_config(test_config_path)

        with open(test_config_path, "rb") as f:
            content = f.read()
            self.assertIn(b'app_name = "Job Analyzer"', content)
            self.assertIn(b'app_author = "Abugh"', content)
            self.assertIn(b'app_log_level = "LogLevel.INFO"', content)

        os.remove(test_config_path)
