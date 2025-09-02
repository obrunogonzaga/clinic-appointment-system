"""
Authentication endpoints for user registration, login, and profile management.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.application.dtos.user_dto import (
    AuthStatusResponse,
    FirstAdminCheckResponse,
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)
from src.application.services.auth_service import AuthService
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.infrastructure.config import get_settings
from src.presentation.api.responses import SuccessResponse
from src.presentation.dependencies.auth import (
    get_auth_service,
    get_current_active_user,
    get_current_admin_user,
)

router = APIRouter()
settings = get_settings()


@router.get(
    "/setup-check",
    response_model=FirstAdminCheckResponse,
    summary="Verificar Setup Inicial",
    description="Verifica se o sistema precisa de configuração inicial do primeiro administrador",
)
async def check_setup(
    auth_service: AuthService = Depends(get_auth_service),
) -> FirstAdminCheckResponse:
    """Check if system needs initial admin setup."""
    return await auth_service.check_first_admin_setup()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Primeiro Admin",
    description="Registra o primeiro usuário administrador do sistema",
)
async def register_first_admin(
    user_data: UserCreateRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register the first admin user."""
    try:
        return await auth_service.register_first_admin(user_data)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de Usuário",
    description="Autentica usuário e retorna token JWT em cookie HttpOnly",
)
async def login(
    response: Response,
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Login user and set JWT cookie."""
    try:
        token_response = await auth_service.login(credentials)
        
        # Set httpOnly cookie with JWT token
        response.set_cookie(
            key="access_token",
            value=token_response.access_token,
            max_age=settings.access_token_expire_minutes * 60,  # Convert to seconds
            expires=token_response.expires_at,
            httponly=True,
            secure=settings.is_production,  # Only HTTPS in production
            samesite="lax",
            path="/"
        )
        
        return token_response
        
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logout de Usuário",
    description="Remove cookie de autenticação",
)
async def logout(response: Response) -> SuccessResponse:
    """Logout user by clearing auth cookie."""
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=settings.is_production,
        httponly=True,
        samesite="lax"
    )
    
    return SuccessResponse(
        success=True,
        message="Logout realizado com sucesso"
    )


@router.get(
    "/me",
    response_model=AuthStatusResponse,
    summary="Perfil do Usuário",
    description="Retorna informações do usuário autenticado",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthStatusResponse:
    """Get current user profile."""
    return await auth_service.get_user_profile(current_user.id)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Usuário",
    description="Cria novo usuário (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def create_user(
    user_data: UserCreateRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Create new user (admin only)."""
    try:
        return await auth_service.register_user(user_data)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/health",
    summary="Health Check de Autenticação",
    description="Verifica se o sistema de autenticação está funcionando",
)
async def auth_health() -> dict[str, Any]:
    """Authentication system health check."""
    return {
        "service": "Authentication Service",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "jwt_auth": True,
            "cookie_auth": True,
            "admin_registration": True,
            "user_management": True,
        }
    }