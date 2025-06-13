"""
Configuration management.

This module provides a centralized way to access configuration settings and
environment variables across the application. It supports different environment
modes (development, staging, production) and provides validation for required
values.

Usage:
    from utils.config import config
    
    # Access configuration values
    api_key = config.OPENAI_API_KEY
    env_mode = config.ENV_MODE
"""

import os
from enum import Enum
from typing import Dict, Any, Optional, get_type_hints, Union
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class EnvMode(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

class Configuration:
    ENV_MODE: EnvMode = EnvMode.LOCAL

    # Redis
    REDIS_HOST: str = "redis-16982.c228.us-central1-1.gce.redns.redis-cloud.com"
    REDIS_PORT: int = 16982
    REDIS_PASSWORD: str = "I5PE5MqGLBE35mGSkQKumgqrSfIjkusE"
    REDIS_SSL: bool = True

    # Daytona
    DAYTONA_API_KEY: str = "dtn_9773988136e99d17b657a2ec09195c43d63da2fd5246287358e5bca3c5e595d8"
    DAYTONA_SERVER_URL: str = "https://app.daytona.io/api"
    DAYTONA_TARGET: str = "9adeeeb2-c8e5-47d5-9e31-f09763fe3ea5"

    # API Keys
    ANTHROPIC_API_KEY: str = "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"
    TAVILY_API_KEY: str = "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"
    RAPID_API_KEY: str = "3ad7245755msh0b7cdddeeabcc92p1c83e4jsnc4a4a44b58c2"
    FIRECRAWL_API_KEY: str = "fc-7978c915339f45dea88f64af937ccfb6"
    FIRECRAWL_URL: Optional[str] = "https://api.firecrawl.dev"

    # Supabase
    SUPABASE_URL: str = "https://oertwiwczbaxsiaqldjl.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    # OpenAI and others (if applicable)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_API_BASE: Optional[str] = "https://openrouter.ai/api/v1"
    OR_SITE_URL: Optional[str] = "https://atlas.ai"
    OR_APP_NAME: Optional[str] = "Atlas AI"

    # Model
    MODEL_TO_USE: Optional[str] = "anthropic/claude-3-7-sonnet-latest"

    def __init__(self):
        load_dotenv()
        env_mode_str = os.getenv("ENV_MODE", EnvMode.LOCAL.value)
        try:
            self.ENV_MODE = EnvMode(env_mode_str.lower())
        except ValueError:
            logger.warning(f"Invalid ENV_MODE: {env_mode_str}, defaulting to LOCAL")
            self.ENV_MODE = EnvMode.LOCAL
        self._load_from_env()
        self._validate()

    def _load_from_env(self):
        for key, expected_type in get_type_hints(self.__class__).items():
            env_val = os.getenv(key)
            if env_val is not None:
                if expected_type == bool:
                    setattr(self, key, env_val.lower() in ('true', 't', 'yes', 'y', '1'))
                elif expected_type == int:
                    try:
                        setattr(self, key, int(env_val))
                    except ValueError:
                        logger.warning(f"Invalid value for {key}: {env_val}, using default")
                elif expected_type == EnvMode:
                    pass
                else:
                    setattr(self, key, env_val)

    def _validate(self):
        type_hints = get_type_hints(self.__class__)
        missing_fields = []
        for field, field_type in type_hints.items():
            is_optional = hasattr(field_type, "__origin__") and field_type.__origin__ is Union and type(None) in field_type.__args__
            if not is_optional and getattr(self, field) is None:
                missing_fields.append(field)
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def as_dict(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key) 
            for key in get_type_hints(self.__class__).keys()
            if not key.startswith('_')
        }

config = Configuration()
