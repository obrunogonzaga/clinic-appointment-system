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
        env_file=[".env", "../.env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Map environment variables to field names
        env_nested_delimiter="__",
        env_prefix="",
        env_alias_generator=None,
        extra="ignore",  # Ignore extra fields from deployment platforms like Coolify
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

    # Server settings
    port: int = Field(
        default=8000,
        description="Porta do servidor",
        validation_alias="PORT",
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
        description="Chave secreta principal",
        validation_alias="JWT_SECRET_KEY",
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

    # Cloudflare R2 / patient documents
    r2_account_id: Optional[str] = Field(
        default=None,
        description="Identificador da conta Cloudflare R2",
        validation_alias="R2_ACCOUNT_ID",
    )
    r2_access_key_id: Optional[str] = Field(
        default=None,
        description="Access key do bucket de documentos",
        validation_alias="R2_ACCESS_KEY_ID",
    )
    r2_secret_access_key: Optional[str] = Field(
        default=None,
        description="Secret key do bucket de documentos",
        validation_alias="R2_SECRET_ACCESS_KEY",
    )
    r2_bucket_patient_docs: str = Field(
        default="",
        description="Bucket onde os documentos de pacientes são armazenados",
        validation_alias="R2_BUCKET_PATIENT_DOCS",
    )
    r2_presign_ttl_seconds: int = Field(
        default=600,
        description="Tempo de expiração das URLs pré-assinadas em segundos",
        validation_alias="R2_PRESIGN_TTL_SECONDS",
    )
    patient_doc_max_upload_mb: int = Field(
        default=10,
        description="Tamanho máximo (MB) permitido para upload de documentos",
        validation_alias="MAX_UPLOAD_MB",
        ge=1,
    )
    allowed_mime_list: List[str] = Field(
        default_factory=lambda: [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
        ],
        description="Lista de MIME types permitidos para documentos",
        validation_alias="ALLOWED_MIME_LIST",
    )
    s3_endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint S3 compatível (MinIO local ou R2)",
        validation_alias="S3_ENDPOINT",
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

    max_tags_per_appointment: int = Field(
        default=5,
        description="Quantidade máxima de tags que podem ser vinculadas a um agendamento",
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
    smtp_from_name: str = Field(
        default="Sistema de Coleta",
        description="Nome do remetente de email",
    )
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="URL de conexão do Redis",
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Senha do Redis",
    )
    redis_db: int = Field(
        default=0,
        description="Database do Redis",
    )
    
    # Enhanced security settings
    email_verification_expire_hours: int = Field(
        default=24,
        description="Tempo de expiração do token de verificação de email em horas",
    )
    password_reset_expire_hours: int = Field(
        default=1,
        description="Tempo de expiração do token de redefinição de senha em horas",
    )
    max_login_attempts: int = Field(
        default=5,
        description="Número máximo de tentativas de login antes do bloqueio",
    )
    account_lock_minutes: int = Field(
        default=30,
        description="Tempo de bloqueio da conta em minutos",
    )
    
    # Rate limiting settings
    rate_limit_enabled: bool = Field(
        default=True,
        description="Habilitar rate limiting",
    )
    login_rate_limit: str = Field(
        default="5/minute",
        description="Rate limit para endpoint de login",
    )
    register_rate_limit: str = Field(
        default="3/hour",
        description="Rate limit para endpoint de registro",
    )
    api_rate_limit: str = Field(
        default="100/minute",
        description="Rate limit global da API",
    )
    verification_rate_limit: str = Field(
        default="2/hour",
        description="Rate limit para verificação de email",
    )
    
    # Frontend URL
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="URL do frontend para links em emails",
    )
    
    # Admin notification settings
    admin_notification_emails: Optional[str] = Field(
        default=None,
        description="Emails dos admins para notificações (separados por vírgula)",
    )

    # Admin email whitelist for security
    admin_email_whitelist: Optional[List[str]] = Field(
        default=None,
        description="Lista de emails autorizados para criar contas administrativas",
        validation_alias="ADMIN_EMAIL_WHITELIST",
    )

    # OpenRouter API settings (for address normalization)
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key para normalização de endereços",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL da API do OpenRouter",
    )
    openrouter_model: str = Field(
        default="openai/gpt-oss-20b:free",
        description="Modelo do OpenRouter para normalização",
    )

    # Address normalization settings
    address_normalization_enabled: bool = Field(
        default=True,
        description="Habilitar normalização automática de endereços",
    )
    address_normalization_batch_size: int = Field(
        default=10,
        description="Tamanho do lote para normalização de endereços",
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

    @field_validator("admin_email_whitelist", mode="before")
    @classmethod
    def validate_admin_email_whitelist(cls, v) -> Optional[List[str]]:
        """Validate and parse admin email whitelist from environment variable."""
        if v is None or v == "":
            return None

        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    # Normalize emails to lowercase and strip whitespace
                    return [
                        email.lower().strip()
                        for email in parsed
                        if isinstance(email, str)
                    ]
                else:
                    # If not a list, treat as single email
                    return [v.lower().strip()]
            except json.JSONDecodeError:
                # If not valid JSON, split by comma
                if "," in v:
                    return [
                        email.lower().strip()
                        for email in v.split(",")
                        if email.strip()
                    ]
                else:
                    return [v.lower().strip()]
        elif isinstance(v, list):
            # Normalize emails to lowercase and strip whitespace
            return [
                email.lower().strip() for email in v if isinstance(email, str)
            ]

        return None

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

    @field_validator("allowed_mime_list", mode="before")
    @classmethod
    def _parse_allowed_mime_list(
        cls, value: Any
    ) -> List[str] | Any:  # type: ignore[override]
        """Allow comma separated values for MIME list env var."""

        if isinstance(value, str):
            items = [item.strip() for item in value.split(",") if item.strip()]
            return items
        return value

    @property
    def patient_doc_max_upload_bytes(self) -> int:
        """Return maximum upload size for patient documents in bytes."""

        return int(self.patient_doc_max_upload_mb) * 1024 * 1024

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
            "openrouter_api_key",
            "admin_email_whitelist",
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
