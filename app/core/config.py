from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BioSum Reliable"
    app_env: str = Field(default="dev")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    max_input_chars: int = Field(default=120000)
    default_summary_sentences: int = Field(default=6)
    max_summary_sentences: int = Field(default=12)
    enable_abstractive: bool = Field(default=False)
    hf_model_name: str = Field(default="sshleifer/distilbart-cnn-12-6")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
