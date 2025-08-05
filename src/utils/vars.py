import os
import pathlib


AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
GITHUB_API_KEY = "GITHUB_API_KEY"
TOML_CONFIG_PATH = "TOML_CONFIG_PATH"
LAYOFF_DB_URL = "LAYOFF_DB_URL"
NEWS_API_KEY = "NEWS_API_KEY"
GOOGLE_SEARCH_API_KEY = "GOOGLE_SEARCH_API_KEY"
LANGSEARCH_API_KEY = "LANGSEARCH_API_KEY"
RAPID_API_KEY = "RAPID_API_KEY"


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


def get_google_search_api_key() -> str:
    """Get Google Search API Key"""

    google_api_key = os.environ.get(GOOGLE_SEARCH_API_KEY)

    if google_api_key:
        return google_api_key

    raise EnvironmentError("GOOGLE_SEARCH_API_KEY not found")


def get_langsearch_api_key() -> str:
    """Get LangSearch API Key"""

    langsearch_api_key = os.environ.get(LANGSEARCH_API_KEY)

    if langsearch_api_key:
        return langsearch_api_key

    raise EnvironmentError("LANGSEARCH_API_KEY not found")


def get_rapid_api_key() -> str:
    """Get Rapid API Key"""

    rapid_api_key = os.environ.get(RAPID_API_KEY)

    if rapid_api_key:
        return rapid_api_key

    raise EnvironmentError("RAPID_API_KEY not found")


def get_layoff_db() -> str:
    """Get LayOff DB Login Info"""

    layoff_db_url = os.environ.get(LAYOFF_DB_URL)

    if layoff_db_url:
        return layoff_db_url

    raise EnvironmentError("LAYOFF_DB_URL not found")


def get_news_api_key() -> str:
    """Get News API Key"""

    news_api_key = os.environ.get(NEWS_API_KEY)

    if news_api_key:
        return news_api_key

    raise EnvironmentError("NEWS_API_KEY not found")
