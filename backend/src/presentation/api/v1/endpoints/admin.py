"""
Admin endpoints for user management and system administration.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dtos.user_dto import (
    PendingUsersResponse,
    UserEnhancedResponse,
    UserApprovalRequest,
    UserRejectionRequest,
    DashboardStatsResponse,
)
from src.application.services.auth_service import AuthService
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.presentation.api.responses import SuccessResponse
from src.presentation.dependencies.auth import (
    get_auth_service,
    get_current_admin_user,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users/pending",
    response_model=PendingUsersResponse,
    summary="Listar Usuários Pendentes",
    description="Lista todos os usuários aguardando aprovação (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_pending_users(
    limit: int = 10,
    offset: int = 0,
    auth_service: AuthService = Depends(get_auth_service),
) -> PendingUsersResponse:
    """Get list of users pending approval."""
    try:
        return await auth_service.get_pending_users(limit, offset)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/users/pending/count",
    response_model=dict,
    summary="Contador de Pendentes",
    description="Retorna quantidade de usuários aguardando aprovação",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_pending_count(
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, int]:
    """Get count of pending users."""
    try:
        pending_users = await auth_service.get_pending_users(limit=1, offset=0)
        return {"count": pending_users.total}
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/users/{user_id}/approve",
    response_model=UserEnhancedResponse,
    summary="Aprovar Usuário",
    description="Aprova um usuário pendente (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def approve_user(
    user_id: str,
    request: UserApprovalRequest,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEnhancedResponse:
    """Approve a pending user."""
    try:
        return await auth_service.approve_user(user_id, current_user, request)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/users/{user_id}/reject",
    response_model=UserEnhancedResponse,
    summary="Rejeitar Usuário",
    description="Rejeita um usuário pendente com motivo (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def reject_user(
    user_id: str,
    request: UserRejectionRequest,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEnhancedResponse:
    """Reject a pending user."""
    try:
        return await auth_service.reject_user(user_id, current_user, request)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/users/{user_id}/details",
    response_model=UserEnhancedResponse,
    summary="Detalhes do Usuário",
    description="Retorna detalhes completos de um usuário para revisão (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_user_details(
    user_id: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEnhancedResponse:
    """Get detailed user information."""
    try:
        # Get user from repository
        user = await auth_service.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Convert to enhanced response if it's a UserEnhanced
        from src.domain.entities.user_enhanced import UserEnhanced
        if isinstance(user, UserEnhanced):
            return auth_service._user_to_enhanced_response(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário não possui informações aprimoradas"
            )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/dashboard/stats",
    response_model=DashboardStatsResponse,
    summary="Estatísticas do Dashboard",
    description="Retorna estatísticas gerais do sistema para o dashboard admin",
    dependencies=[Depends(get_current_admin_user)],
)
async def get_dashboard_stats(
    auth_service: AuthService = Depends(get_auth_service),
) -> DashboardStatsResponse:
    """Get dashboard statistics."""
    try:
        return await auth_service.get_dashboard_stats()
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/health",
    summary="Health Check Admin",
    description="Verifica se o sistema admin está funcionando",
)
async def admin_health() -> dict[str, Any]:
    """Admin system health check."""
    return {
        "service": "Admin Service",
        "status": "healthy",
        "features": {
            "user_approval": True,
            "dashboard_stats": True,
            "user_management": True,
        },
    }