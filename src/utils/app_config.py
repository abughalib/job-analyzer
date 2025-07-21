import tomllib
import tomli_w
from enum import Enum
from pydantic import BaseModel
from pathlib import Path

from utils.vars import app_config_path


class Hosted(Enum):
    LOCALLY_HOSTED = "LOCALLY_HOSTED"
    AZURE_HOSTED = "AZURE_HOSTED"

    def to_string(self) -> str:
        """Convert Hosted to string representation."""
        return f"Hosted.{self.name}"

    @staticmethod
    def from_string(value: str) -> "Hosted":
        if value == "Hosted.LOCALLY_HOSTED":
            return Hosted.LOCALLY_HOSTED
        elif value == "Hosted.AZURE_HOSTED":
            return Hosted.AZURE_HOSTED
        else:
            raise ValueError(f"Unknown Hosted type: {value}")


class PostgreSQLConfig(BaseModel):
    database: str = "search_db"
    hostname: str = "localhost"
    port: int = 5432


class ChromaConfig(BaseModel):
    collection_name: str = "search_db"
    hostname: str
    port: str


class DatabaseEngine(Enum):
    CHROMA_DB = "CHROMA_DB"
    POSTGRESQL = "POSTGRESQL"
    WEAVIATE = "WEAVIATE"

    def to_string(self) -> str:
        """Convert DatabaseEngine to string representation."""
        return f"DatabaseEngine.{self.name}"

    @staticmethod
    def from_string(value: str) -> "DatabaseEngine":
        if value == "DatabaseEngine.CHROMA_DB":
            return DatabaseEngine.CHROMA_DB
        elif value == "DatabaseEngine.POSTGRESQL":
            return DatabaseEngine.POSTGRESQL
        elif value == "DatabaseEngine.WEAVIATE":
            return DatabaseEngine.WEAVIATE
        else:
            raise ValueError(f"Unknown DatabaseEngine: {value}")


class WeaviateConfig(BaseModel):
    url: str = "http://localhost:8080"
    database_name: str = "search_db"
    class_name: str = "Document"
    vector_index_name: str = "DocumentVectorIndex"


class DatabaseConfig(BaseModel):
    """Database Configuration"""

    database_engine: DatabaseEngine = DatabaseEngine.POSTGRESQL
    database_config: PostgreSQLConfig | ChromaConfig | WeaviateConfig = (
        PostgreSQLConfig()
    )
    hosted: Hosted = Hosted.LOCALLY_HOSTED

    @staticmethod
    def default() -> "DatabaseConfig":
        """Default configuration for the database"""
        return DatabaseConfig(
            database_engine=DatabaseEngine.POSTGRESQL,
            database_config=PostgreSQLConfig(),
            hosted=Hosted.LOCALLY_HOSTED,
        )


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def to_string(self) -> str:
        """Convert LogLevel to string representation."""
        return f"LogLevel.{self.name}"

    @staticmethod
    def default() -> "LogLevel":
        """Default log level"""
        return LogLevel.INFO

    @staticmethod
    def from_string(value: str) -> "LogLevel":
        if value == "LogLevel.DEBUG":
            return LogLevel.DEBUG
        elif value == "LogLevel.INFO":
            return LogLevel.INFO
        elif value == "LogLevel.WARNING":
            return LogLevel.WARNING
        elif value == "LogLevel.ERROR":
            return LogLevel.ERROR
        elif value == "LogLevel.CRITICAL":
            return LogLevel.CRITICAL
        else:
            raise ValueError(f"Unknown LogLevel: {value}")


class AppSetting(BaseModel):
    """App specific settings"""

    app_name: str = "Job Analyzer"
    app_author: str = "Abugh"
    app_log_level: LogLevel = LogLevel.INFO

    @staticmethod
    def default() -> "AppSetting":
        """Default configuration for the app settings"""
        return AppSetting(
            app_name="Job Analyzer",
            app_author="Abugh",
            app_log_level=LogLevel.default(),
        )


class AppConfig:

    def __init__(self):
        self.database_config: DatabaseConfig = DatabaseConfig.default()
        self.app_setting: AppSetting = AppSetting.default()

    def save_config(self, toml_file_path: Path = app_config_path()):

        with open(toml_file_path, "wb") as f:
            tomli_w.dump(self.dict(), f)
            f.close()

    def dict(self):
        db_conf = self.database_config.model_dump()
        db_conf["database_engine"] = db_conf["database_engine"].to_string()
        db_conf["hosted"] = db_conf["hosted"].to_string()

        app_set = self.app_setting.model_dump()
        app_set["app_log_level"] = app_set["app_log_level"].to_string()

        return {
            "database_config": db_conf,
            "app_setting": app_set,
        }

    @staticmethod
    def default() -> "AppConfig":
        """Default configuration for the app"""
        return AppConfig()

    @staticmethod
    def from_config(path: Path = app_config_path()) -> "AppConfig":

        with open(path, "rb") as f:

            try:
                config = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"Error decoding TOML file at {path}: {e}")

        if not config:
            return AppConfig.default()

        return AppConfig.default()
