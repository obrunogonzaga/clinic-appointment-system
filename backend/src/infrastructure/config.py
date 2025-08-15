"""
Application configuration management using Pydantic Settings.
"""

import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation and environment variable support.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Map environment variables to field names
        env_nested_delimiter="__",
        env_prefix="",
        env_alias_generator=None,
    )

    # Application settings
    app_name: str = Field(
        default="Clinic Appointment System API",
        description="Nome da aplicação",
    )
    app_version: str = Field(
        default="1.0.0",
        description="Versão da aplicação",
    )
    debug: bool = Field(
        default=False,
        description="Modo debug",
    )
    environment: str = Field(
        default="development",
        description="Ambiente de execução (development, staging, production)",
    )

    # API settings
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="Prefixo da API v1",
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Origens permitidas para CORS",
        validation_alias="CORS_ORIGINS",
    )

    # Database settings
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="URL de conexão do MongoDB",
    )
    database_name: str = Field(
        default="clinic_db",
        description="Nome do banco de dados",
    )

    # Security settings
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Chave secreta para JWT",
    )
    algorithm: str = Field(
        default="HS256",
        description="Algoritmo de criptografia JWT",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Tempo de expiração do token de acesso em minutos",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Tempo de expiração do token de atualização em dias",
    )

    # Password settings
    password_min_length: int = Field(
        default=8,
        description="Comprimento mínimo da senha",
    )
    password_require_uppercase: bool = Field(
        default=True,
        description="Requer letra maiúscula na senha",
    )
    password_require_lowercase: bool = Field(
        default=True,
        description="Requer letra minúscula na senha",
    )
    password_require_numbers: bool = Field(
        default=True,
        description="Requer números na senha",
    )
    password_require_special: bool = Field(
        default=True,
        description="Requer caracteres especiais na senha",
    )

    # File upload settings
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamanho máximo de upload em bytes",
    )
    allowed_upload_extensions: List[str] = Field(
        default=[".csv", ".xls", ".xlsx"],
        description="Extensões permitidas para upload",
    )

    # Pagination settings
    default_page_size: int = Field(
        default=20,
        description="Tamanho padrão da página",
    )
    max_page_size: int = Field(
        default=100,
        description="Tamanho máximo da página",
    )

    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="json",
        description="Formato do log (json, text)",
    )

    # Email settings (optional, for notifications)
    smtp_host: Optional[str] = Field(
        default=None,
        description="Host do servidor SMTP",
    )
    smtp_port: Optional[int] = Field(
        default=587,
        description="Porta do servidor SMTP",
    )
    smtp_username: Optional[str] = Field(
        default=None,
        description="Usuário SMTP",
    )
    smtp_password: Optional[str] = Field(
        default=None,
        description="Senha SMTP",
    )
    smtp_from_email: Optional[str] = Field(
        default=None,
        description="Email remetente padrão",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def validate_allowed_origins(cls, v) -> List[str]:
        """Validate and parse CORS origins from environment variable."""
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                else:
                    # If not a list, treat as single origin
                    return [v]
            except json.JSONDecodeError:
                # If not valid JSON, split by comma or treat as single origin
                if "," in v:
                    return [origin.strip() for origin in v.split(",")]
                else:
                    return [v.strip()]
        elif isinstance(v, list):
            return v
        else:
            return ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    def get_database_url(self) -> str:
        """Get the full database URL with database name."""
        return f"{self.mongodb_url}/{self.database_name}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary, excluding sensitive information.
        """
        data = self.model_dump()
        # Remove sensitive fields
        sensitive_fields = [
            "secret_key",
            "mongodb_url",
            "smtp_password",
            "smtp_username",
        ]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***"
        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()
