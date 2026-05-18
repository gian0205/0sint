"""Application settings (env-driven)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OSINT_", extra="ignore")

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60

    admin_token: str = "dev-admin-token-change-me"

    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 1024

    rate_limit_per_minute: int = 30

    audit_log_path: str = "audit.log"


settings = Settings()
