import os
import pathlib
from unittest import TestCase

from utils.vars import (
    app_config_path,
    get_azure_openai_key,
    get_github_api_key,
)


class TestVars(TestCase):
    """Test cases for utility variables and functions in vars.py"""

    def test_app_config_default_path(self):
        """Test the app_config_path function"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assertEqual(
            app_config_path(),
            pathlib.Path(current_dir).parent.parent
            / "src"
            / "config"
            / "app_config.toml",
        )

    def test_app_config_path_env(self):
        """Test the app_config_path function with environment variable set"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        custom_path = pathlib.Path(current_dir).parent.parent / "custom_config.toml"
        os.environ["TOML_CONFIG_PATH"] = str(custom_path)

        self.assertEqual(app_config_path(), custom_path)
        del os.environ["TOML_CONFIG_PATH"]

    def test_get_azure_openai_key(self):
        """Test the get_azure_openai_key function"""
        with self.assertRaises(EnvironmentError):
            get_azure_openai_key()

    def test_get_github_api_key(self):
        """Test the get_github_api_key function"""
        with self.assertRaises(EnvironmentError):
            get_github_api_key()

    def test_get_azure_openai_key_with_env(self):
        """Test the get_azure_openai_key function with environment variable set"""
        key = "test_azure_openai_key"
        os.environ["AZURE_OPENAI_KEY"] = key
        self.assertEqual(get_azure_openai_key(), key)
        del os.environ["AZURE_OPENAI_KEY"]

    def test_get_github_api_key_with_env(self):
        key = "test_github_api_key"
        os.environ["GITHUB_API_KEY"] = key
        self.assertEqual(get_github_api_key(), key)
        del os.environ["GITHUB_API_KEY"]
