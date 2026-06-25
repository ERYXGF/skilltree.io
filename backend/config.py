"""Application settings loaded from environment / .env."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")
    github_token: str = Field(default="", description="Optional GitHub personal access token")
    model_name: str = Field(default="claude-sonnet-4-6", description="Claude model id")
    db_path: str = Field(default="skilltree.db", description="SQLite database path")


def get_settings() -> Settings:
    return Settings()
