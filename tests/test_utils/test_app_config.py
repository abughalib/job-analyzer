import os
from pathlib import Path
from unittest import TestCase

from utils.app_config import AppConfig, LogLevel


class TestAppConfig(TestCase):
    """Test cases for application configuration settings."""

    def setUp(self):
        """Set up the test environment."""
        self.app_config = AppConfig.default()
        self.test_dir = Path(__file__).parent
        self.test_dir.mkdir(exist_ok=True)

    def test_load_default_config(self):
        """Test loading the default configuration."""
        self.assertIsInstance(self.app_config, AppConfig)
        self.assertEqual(self.app_config.app_setting.app_name, "Job Analyzer")
        self.assertEqual(self.app_config.app_setting.app_author, "Abugh")
        self.assertEqual(self.app_config.app_setting.app_log_level, LogLevel.INFO)

    def test_save_and_load_config(self):
        """Test saving configuration to a TOML file and loading it back."""
        test_config_path = self.test_dir / "test_config_runtime.toml"

        self.app_config.app_setting.app_log_level = LogLevel.DEBUG
        self.app_config.app_setting.app_name = "Test App"

        self.app_config.save_config(test_config_path)

        with open(test_config_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('app_name = "Test App"', content)
            self.assertIn('app_author = "Abugh"', content)
            self.assertIn('app_log_level = "DEBUG"', content)
            self.assertNotIn("dimension =", content)
        loaded_config = AppConfig.from_config(test_config_path)
        self.assertEqual(loaded_config.app_setting.app_log_level, LogLevel.DEBUG)
        self.assertEqual(loaded_config.app_setting.app_name, "Test App")

        os.remove(test_config_path)
