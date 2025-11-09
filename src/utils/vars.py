import os
import pathlib
import logging


logger = logging.getLogger(__name__)

AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
OPENAI_KEY = "OPENAI_KEY"
GITHUB_API_KEY = "GITHUB_API_KEY"
TOML_CONFIG_PATH = "TOML_CONFIG_PATH"
LAYOFF_DB_URL = "LAYOFF_DB_URL"
NEWS_API_KEY = "NEWS_API_KEY"
GOOGLE_SEARCH_API_KEY = "GOOGLE_SEARCH_API_KEY"
LANGSEARCH_API_KEY = "LANGSEARCH_API_KEY"
RAPID_API_KEY = "RAPID_API_KEY"
GEMINI_API_KEY = "GEMINI_API_KEY"


def app_config_path() -> pathlib.Path:
    """Get App Configuration TOML file Path"""
    logger.debug("Resolving app configuration path")

    toml_config_path = os.environ.get(TOML_CONFIG_PATH)
    if toml_config_path:
        logger.debug(f"Using config path from environment: {toml_config_path}")
        return pathlib.Path(toml_config_path)

    # Use the default path if not set
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = pathlib.Path(current_dir).parent / "config" / "app_config.toml"
    logger.debug(f"Using default config path: {default_path}")
    return default_path


def get_app_path() -> pathlib.Path:
    """Get the App Path"""
    logger.debug("Resolving application root path")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = pathlib.Path(current_dir).parent.parent
    logger.debug(f"Application root path resolved to: {app_path}")
    return app_path


def get_azure_openai_key() -> str:
    """Get Azure OpenAI Key"""
    logger.debug("Retrieving Azure OpenAI API key")

    azure_api_key = os.environ.get(AZURE_OPENAI_KEY)
    if azure_api_key:
        logger.debug("Azure OpenAI API key found in environment")
        return azure_api_key

    logger.error("Azure OpenAI API key not found in environment variables")
    raise EnvironmentError("AZURE_OPENAI_KEY not found")


def get_openai_key() -> str:
    """Get OpenAI Key"""
    logger.debug("Retrieving OpenAI API key")

    open_api_key = os.environ.get(OPENAI_KEY)
    if open_api_key:
        logger.debug("OpenAI API key found in environment")
        return open_api_key

    logger.error("OpenAI API key not found in environment variables")
    raise EnvironmentError("OPENAI_KEY not found")


def get_github_api_key() -> str:
    """Get GitHub API Key"""
    logger.debug("Retrieving GitHub API key")

    github_api_key = os.environ.get(GITHUB_API_KEY)
    if github_api_key:
        logger.debug("GitHub API key found in environment")
        return github_api_key

    logger.error("GitHub API key not found in environment variables")
    raise EnvironmentError("GitHub API Key not Found")


def get_google_search_api_key() -> str:
    """Get Google Search API Key"""
    logger.debug("Retrieving Google Search API key")

    google_api_key = os.environ.get(GOOGLE_SEARCH_API_KEY)
    if google_api_key:
        logger.debug("Google Search API key found in environment")
        return google_api_key

    logger.error("Google Search API key not found in environment variables")
    raise EnvironmentError("GOOGLE_SEARCH_API_KEY not found")


def get_langsearch_api_key() -> str:
    """Get LangSearch API Key"""
    logger.debug("Retrieving LangSearch API key")

    langsearch_api_key = os.environ.get(LANGSEARCH_API_KEY)
    if langsearch_api_key:
        logger.debug("LangSearch API key found in environment")
        return langsearch_api_key

    logger.error("LangSearch API key not found in environment variables")
    raise EnvironmentError("LANGSEARCH_API_KEY not found")


def get_rapid_api_key() -> str:
    """Get Rapid API Key"""
    logger.debug("Retrieving Rapid API key")

    rapid_api_key = os.environ.get(RAPID_API_KEY)
    if rapid_api_key:
        logger.debug("Rapid API key found in environment")
        return rapid_api_key

    logger.error("Rapid API key not found in environment variables")
    raise EnvironmentError("RAPID_API_KEY not found")


def get_gemini_api_key() -> str:
    """Get Gemini API Key"""
    logger.debug("Retrieving Gemini API key")

    gemini_api_key = os.environ.get(GEMINI_API_KEY)
    if gemini_api_key:
        logger.debug("Gemini API key found in environment")
        return gemini_api_key

    logger.error("Gemini API key not found in environment variables")
    raise EnvironmentError("GEMINI_API_KEY not found")


def get_layoff_db() -> str:
    """Get LayOff DB Login Info"""
    logger.debug("Retrieving LayOff DB URL")

    layoff_db_url = os.environ.get(LAYOFF_DB_URL)
    if layoff_db_url:
        logger.debug("LayOff DB URL found in environment")
        return layoff_db_url

    logger.error("LayOff DB URL not found in environment variables")
    raise EnvironmentError("LAYOFF_DB_URL not found")


def get_news_api_key() -> str:
    """Get News API Key"""
    logger.debug("Retrieving News API key")

    news_api_key = os.environ.get(NEWS_API_KEY)
    if news_api_key:
        logger.debug("News API key found in environment")
        return news_api_key

    logger.error("News API key not found in environment variables")
    raise EnvironmentError("NEWS_API_KEY not found")
