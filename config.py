"""
config.py — Environment configuration for C365 CS Agent
All secrets are loaded from environment variables. Never hardcode credentials.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "C365 CS Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    port: int = 8000

    # ── Anthropic / Claude ───────────────────────────────────────────────────
    anthropic_api_key: str = ""
    claude_model_classify: str = "claude-sonnet-4-6"
    claude_model_respond: str = "claude-sonnet-4-6"
    claude_max_tokens: int = 1024

    # ── Zendesk ──────────────────────────────────────────────────────────────
    zendesk_subdomain: str = "demo"
    zendesk_email: str = "demo@conveyance365.com"
    zendesk_api_token: str = ""

    # ── Microsoft Graph / Outlook ─────────────────────────────────────────────
    ms_tenant_id: str = ""
    ms_client_id: str = ""
    ms_client_secret: str = ""
    ms_mailbox: str = "demo@conveyance365.com"
    ms_graph_scope: str = "https://graph.microsoft.com/.default"

    # ── Azure App Service ─────────────────────────────────────────────────────
    # These are set automatically by App Service; override locally if needed.
    website_hostname: str = "localhost"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
