import os
import pathlib


AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
GITHUB_API_KEY = "GITHUB_API_KEY"
TOML_CONFIG_PATH = "TOML_CONFIG_PATH"


def app_config_path() -> pathlib.Path:
    toml_config_path = os.environ.get(TOML_CONFIG_PATH)

    if toml_config_path:
        return pathlib.Path(toml_config_path)

    # Use the default path if not set

    current_dir = os.path.dirname(os.path.abspath(__file__))

    return pathlib.Path(current_dir).parent / "config" / "app_config.toml"


def get_azure_openai_key() -> str:

    azure_api_key = os.environ.get(AZURE_OPENAI_KEY)

    if azure_api_key:

        return azure_api_key

    raise EnvironmentError("AZURE_OPENAI_KEY not found")


def get_github_api_key() -> str:

    github_api_key = os.environ.get(GITHUB_API_KEY)

    if github_api_key:
        return github_api_key

    raise EnvironmentError("GitHub API Key not Found")
