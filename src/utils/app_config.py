import tomllib
import tomli_w
from enum import Enum
from pydantic import BaseModel, Field
from pathlib import Path

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
    max_tokens: int = 4096
    context_window: int = 4096


class AzureOpenAIInferenceConfig(BaseModel):
    api_base: str = "https://api.openai.azure.com/"
    api_version: str = "2023-05-15"
    model: str = "gpt-35-turbo"
    temperature: float = 0.7
    max_tokens: int = 4096
    deployment_name: str = "gpt-35-turbo"
    context_window: int = 4096


class GeminiInferenceConfig(BaseModel):
    api_base: str = "https://api.gemini.com/v1"
    model: str = "gemma-3-27b-it"
    temperature: float = 0.6
    max_tokens: int = 4096
    context_window: int = 131072


class LocalInferenceConfig(BaseModel):
    api_base: str = "http://localhost:1234/v1/chat/completions"
    model: str = "models/model.gguf"
    tokenizer: str = "models/tokenizer.json"
    temperature: float = 0.7
    max_tokens: int = 4096
    context_window: int = 4096
    use_gpu: bool = True


class InferenceConfig(BaseModel):
    openai: OpenAIInferenceConfig = OpenAIInferenceConfig()
    azure_openai: AzureOpenAIInferenceConfig = AzureOpenAIInferenceConfig()
    local: LocalInferenceConfig = LocalInferenceConfig()
    gemini: GeminiInferenceConfig = GeminiInferenceConfig()


class Inference(BaseModel):
    hosted: ModelHosted = ModelHosted.OPENAI_HOSTED
    inference_engine: InferenceEngine = InferenceEngine.OPENAI
    inference_config: InferenceConfig = Field(default_factory=InferenceConfig)

    @staticmethod
    def default() -> "Inference":
        return Inference()


class AzureEmbeddingConfig(BaseModel):
    api_base: str = "https://api.openai.azure.com/"
    api_version: str = "2023-05-15"
    model: str = "text-embedding-3"
    deployment_name: str = "text-embedding-3"
    dimension: int | None = None


class OpenAIEmbeddingConfig(BaseModel):
    api_base: str = "https://api.openai.com/v1"
    model: str = "text-embedding-3"
    dimension: int | None = None


class GeminiEmbeddingConfig(BaseModel):
    api_base: str = "https://api.gemini.com/v1"
    model: str = "gemini-embed-1"
    dimension: int | None = None


class LocalEmbeddingConfig(BaseModel):
    model: str = "models/embed_model.gguf"
    tokenizer: str = "models/embed_tokenizer.json"
    dimension: int | None = None
    use_gpu: bool = True


class EmbeddingConfig(BaseModel):
    azure_embedding_config: AzureEmbeddingConfig = Field(
        default_factory=AzureEmbeddingConfig
    )
    openai_embedding_config: OpenAIEmbeddingConfig = Field(
        default_factory=OpenAIEmbeddingConfig
    )
    local_embedding_config: LocalEmbeddingConfig = Field(
        default_factory=LocalEmbeddingConfig
    )
    gemini_embedding_config: GeminiEmbeddingConfig = Field(
        default_factory=GeminiEmbeddingConfig
    )


class Embedding(BaseModel):
    hosted: ModelHosted = ModelHosted.OPENAI_HOSTED
    embedding_engine: InferenceEngine = InferenceEngine.OPENAI
    embedding_config: EmbeddingConfig = Field(default_factory=EmbeddingConfig)

    @staticmethod
    def default() -> "Embedding":
        return Embedding()


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
    postgresql_config: PostgreSQLConfig = Field(default_factory=PostgreSQLConfig)
    chroma_config: ChromaConfig = Field(default_factory=ChromaConfig)
    weaviate_config: WeaviateConfig = Field(default_factory=WeaviateConfig)
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
    embed: Embedding = Field(default_factory=Embedding.default)

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

    @classmethod
    def load_default(cls) -> "AppConfig":
        """Loads the default configuration."""
        return cls.from_config(app_config_path())

    @staticmethod
    def default() -> "AppConfig":
        """Provides a default instance of the application configuration."""
        return AppConfig()
