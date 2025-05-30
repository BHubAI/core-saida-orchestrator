import logging
from typing import Any, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # Disable .env file loading
        env_file_encoding="utf-8",
        extra="allow",  # This allows extra fields from environment
    )

    # App settings
    VERSION: str = Field(default="v1")
    ENV: str = Field(default="dev")
    DEBUG: bool = Field(default=False)
    CORE_APP_URL: str = Field(default="")

    # AWS settings(localstack values by default)
    AWS_ENDPOINT_URL: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    CORE_SAIDA_BUCKET_NAME: str = Field(default="core-saida")

    # Camunda settings
    CAMUNDA_ENGINE_URL: str = Field(default="")
    CAMUNDA_USERNAME: str = Field(default="")
    CAMUNDA_PASSWORD: str = Field(default="")
    CAMUNDA_API_TOKEN: str = Field(default="")

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(default=[])
    LOG_LEVEL: int = Field(default=logging.INFO)

    # Datadog settings
    DD_AGENT_HOST: str = Field(default="datadog-agent")
    DD_AGENT_PORT: int = Field(default=8125)
    DD_ENV: str = Field(default="dev")
    DD_SERVICE: str = Field(default="core-saida-orchestrator")
    DD_VERSION: str = Field(default="1.0.0")

    # Database settings
    POSTGRES_USER: str = Field(default="")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_HOST: str = Field(default="")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB: str = Field(default="")

    # Pool settings
    DB_POOL_SIZE: int = Field(default=83)
    WEB_CONCURRENCY: int = Field(default=9)
    MAX_OVERFLOW: int = Field(default=64)
    POOL_SIZE: Optional[int] = Field(default=None)

    # RPA Settings
    MELIUS_RPA_URL: str = Field(default="")
    MELIUS_RPA_TOKEN: str = Field(default="")

    @field_validator("POOL_SIZE", mode="before")
    @classmethod
    def build_pool(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, int):
            return v

        return max(values.data.get("DB_POOL_SIZE") // values.data.get("WEB_CONCURRENCY"), 5)  # type: ignore

    @classmethod
    def build_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str) and len(v) > 0:
            return v

        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        )


settings = Settings()
