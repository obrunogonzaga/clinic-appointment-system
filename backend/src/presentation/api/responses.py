"""
Standard API response models.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    success: bool = Field(
        True, description="Indica se a operação foi bem-sucedida"
    )
    message: Optional[str] = Field(None, description="Mensagem opcional")
    request_id: Optional[str] = Field(
        None, description="ID único da requisição"
    )


class DataResponse(BaseResponse, Generic[T]):
    """Response model with single data item."""

    data: T = Field(..., description="Dados da resposta")


class ListResponse(BaseResponse, Generic[T]):
    """Response model with list of items."""

    data: List[T] = Field(..., description="Lista de itens")
    total: int = Field(..., description="Total de itens")
    page: int = Field(1, description="Página atual")
    per_page: int = Field(20, description="Itens por página")
    pages: int = Field(1, description="Total de páginas")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(1, ge=1, description="Número da página")
    per_page: int = Field(20, ge=1, le=100, description="Itens por página")

    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        """Get limit value for database queries."""
        return self.per_page


class HealthResponse(BaseResponse):
    """Health check response model."""

    status: str = Field("healthy", description="Status do serviço")
    service: str = Field(..., description="Nome do serviço")
    version: str = Field(..., description="Versão do serviço")
    environment: str = Field(..., description="Ambiente de execução")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Detalhes adicionais"
    )
    success: bool = Field(
        True, description="Indica se a operação foi bem-sucedida"
    )
    message: Optional[str] = Field(None, description="Mensagem opcional")


class CreatedResponse(BaseResponse):
    """Response for resource creation."""

    id: str = Field(..., description="ID do recurso criado")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Dados do recurso criado"
    )


class UpdatedResponse(BaseResponse):
    """Response for resource update."""

    id: str = Field(..., description="ID do recurso atualizado")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Dados atualizados"
    )


class DeletedResponse(BaseResponse):
    """Response for resource deletion."""

    id: str = Field(..., description="ID do recurso removido")
    message: str = Field(
        "Recurso removido com sucesso", description="Mensagem de confirmação"
    )
