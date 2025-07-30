import os
import pathlib


AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
GITHUB_API_KEY = "GITHUB_API_KEY"
TOML_CONFIG_PATH = "TOML_CONFIG_PATH"
LAYOFF_DB_URL = "LAYOFF_DB_URL"


def app_config_path() -> pathlib.Path:
    """Get App Configuration TOML file Path"""
    toml_config_path = os.environ.get(TOML_CONFIG_PATH)

    if toml_config_path:
        return pathlib.Path(toml_config_path)

    # Use the default path if not set

    current_dir = os.path.dirname(os.path.abspath(__file__))

    return pathlib.Path(current_dir).parent / "config" / "app_config.toml"


def get_app_path() -> pathlib.Path:
    """Get the App Path"""

    current_dir = os.path.dirname(os.path.abspath(__file__))

    return pathlib.Path(current_dir).parent.parent


def get_azure_openai_key() -> str:
    """Get Azure OpenAI Key"""

    azure_api_key = os.environ.get(AZURE_OPENAI_KEY)

    if azure_api_key:

        return azure_api_key

    raise EnvironmentError("AZURE_OPENAI_KEY not found")


def get_github_api_key() -> str:
    """Get GitHub API Key"""

    github_api_key = os.environ.get(GITHUB_API_KEY)

    if github_api_key:
        return github_api_key

    raise EnvironmentError("GitHub API Key not Found")


def get_layoff_db() -> str:
    """Get LayOff DB Login Info"""

    layoff_db_url = os.environ.get(LAYOFF_DB_URL)

    if layoff_db_url:
        return layoff_db_url

    raise EnvironmentError("LAYOFF_DB_URL not found")
