"""Request context helpers shared across services."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """Simple role definitions supported by the platform."""

    ADMIN = "admin"
    COLLABORATOR = "collaborator"


class RequestContext(BaseModel):
    """Information extracted from the incoming request for auditing."""

    user_id: str = Field(..., description="Identificador do usuário autenticado")
    tenant_id: str = Field(..., description="Tenant associado à requisição")
    role: UserRole = Field(
        default=UserRole.COLLABORATOR,
        description="Perfil de acesso do usuário",
    )
    source_ip: Optional[str] = Field(
        None, description="Endereço IP de origem utilizado para auditoria"
    )
