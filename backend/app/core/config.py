from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LaunchShield AI"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="LAUNCHSHIELD_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
