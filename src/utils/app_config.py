import tomllib
import tomli_w
from enum import Enum
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Union

from utils.vars import app_config_path


class Hosted(str, Enum):
    LOCALLY_HOSTED = "LOCALLY_HOSTED"
    AZURE_HOSTED = "AZURE_HOSTED"


class ModelHosted(str, Enum):
    LOCALLY_HOSTED = "LOCALLY_HOSTED"
    AZURE_HOSTED = "AZURE_HOSTED"
    OPENAI_HOSTED = "OPENAI_HOSTED"
    GOOGLE_HOSTED = "GOOGLE_HOSTED"


class InferenceEngine(str, Enum):
    OPENAI = "OPENAI"
    AZURE_OPENAI = "AZURE_OPENAI"
    LOCAL = "LOCAL"
    GEMINI = "GEMINI"


class DatabaseEngine(str, Enum):
    CHROMA_DB = "CHROMA_DB"
    POSTGRESQL = "POSTGRESQL"
    WEAVIATE = "WEAVIATE"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OpenAIInferenceConfig(BaseModel):
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000


class AzureOpenAIInferenceConfig(BaseModel):
    api_base: str = "https://api.openai.azure.com/"
    api_version: str = "2023-05-15"
    model: str = "gpt-35-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    deployment_name: str = "gpt-35-turbo"


class GeminiInferenceConfig(BaseModel):
    api_base: str = "https://api.gemini.com/v1"
    model: str = "gemini-1"
    temperature: float = 0.7
    max_tokens: int = 1000


class LocalInferenceConfig(BaseModel):
    model_path: str = "models/model.gguf"
    tokenizer_path: str = "models/tokenizer.json"
    temperature: float = 0.7
    max_tokens: int = 1000
    use_gpu: bool = True


class Inference(BaseModel):
    hosted: ModelHosted = ModelHosted.OPENAI_HOSTED
    inference_engine: InferenceEngine = InferenceEngine.OPENAI
    inference_config: Union[
        AzureOpenAIInferenceConfig,
        OpenAIInferenceConfig,
        LocalInferenceConfig,
        GeminiInferenceConfig,
    ] = Field(default_factory=OpenAIInferenceConfig)

    @staticmethod
    def default() -> "Inference":
        return Inference()


class AzureEmbedConfig(BaseModel):
    api_base: str = "https://api.openai.azure.com/"
    api_version: str = "2023-05-15"
    model: str = "text-embedding-3"
    deployment_name: str = "text-embedding-3"
    dimension: int | None = None


class OpenAIEmbedConfig(BaseModel):
    api_base: str = "https://api.openai.com/v1"
    model: str = "text-embedding-3"
    dimension: int | None = None


class GeminiEmbedConfig(BaseModel):
    api_base: str = "https://api.gemini.com/v1"
    model: str = "gemini-embed-1"
    dimension: int | None = None


class LocalEmbedConfig(BaseModel):
    model_path: str = "models/embed_model.gguf"
    tokenizer_path: str = "models/embed_tokenizer.json"
    dimension: int | None = None
    use_gpu: bool = True


class Embed(BaseModel):
    hosted: ModelHosted = ModelHosted.OPENAI_HOSTED
    inference_engine: InferenceEngine = InferenceEngine.OPENAI
    inference_config: Union[
        AzureEmbedConfig, OpenAIEmbedConfig, LocalEmbedConfig, GeminiEmbedConfig
    ] = Field(default_factory=OpenAIEmbedConfig)

    @staticmethod
    def default() -> "Embed":
        return Embed()


class PostgreSQLConfig(BaseModel):
    database: str = "search_db"
    hostname: str = "localhost"
    port: int = 5432


class ChromaConfig(BaseModel):
    collection_name: str = "search_db"
    hostname: str = "localhost"
    port: int = 8000


class WeaviateConfig(BaseModel):
    url: str = "http://localhost:8080"
    database_name: str = "search_db"
    class_name: str = "Document"
    vector_index_name: str = "DocumentVectorIndex"


class DatabaseConfig(BaseModel):
    database_engine: DatabaseEngine = DatabaseEngine.POSTGRESQL
    database_config: Union[PostgreSQLConfig, ChromaConfig, WeaviateConfig] = Field(
        default_factory=PostgreSQLConfig
    )
    hosted: Hosted = Hosted.LOCALLY_HOSTED

    @staticmethod
    def default() -> "DatabaseConfig":
        return DatabaseConfig()


class AppSetting(BaseModel):
    app_name: str = "Job Analyzer"
    app_author: str = "Abugh"
    app_log_level: LogLevel = LogLevel.INFO

    @staticmethod
    def default() -> "AppSetting":
        return AppSetting()


class AppConfig(BaseModel):
    """Main application configuration model, powered by Pydantic."""

    database_config: DatabaseConfig = Field(default_factory=DatabaseConfig.default)
    app_setting: AppSetting = Field(default_factory=AppSetting.default)
    inference: Inference = Field(default_factory=Inference.default)
    embed: Embed = Field(default_factory=Embed.default)

    def save_config(self, toml_file_path: Path = app_config_path()):
        """Saves the configuration to a TOML file."""
        config_dict = self.model_dump(mode="json", exclude_none=True)

        toml_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(toml_file_path, "wb") as f:
            tomli_w.dump(config_dict, f)
        print(f"Configuration saved to {toml_file_path}")

    @classmethod
    def from_config(cls, path: Path = app_config_path()) -> "AppConfig":
        """Loads configuration from a TOML file."""
        if not path.exists():
            print("No config file found, returning default configuration.")
            return cls.default()

        with open(path, "rb") as f:
            try:
                config_data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"Error decoding TOML file at {path}: {e}")

        print(f"Configuration loaded from {path}")
        return cls(**config_data)

    @staticmethod
    def default() -> "AppConfig":
        """Provides a default instance of the application configuration."""
        return AppConfig()
