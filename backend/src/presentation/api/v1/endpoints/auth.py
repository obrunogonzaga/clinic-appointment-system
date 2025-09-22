"""
Authentication endpoints for user registration, login, and profile management.
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.application.dtos.user_dto import (
    AuthStatusResponse,
    FirstAdminCheckResponse,
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
    UserListRequest,
    UserListResponse,
    UserUpdateRequest,
    PublicUserRegisterRequest,
    UserEnhancedResponse,
    EmailVerificationRequest,
    ResendVerificationRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
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
from src.presentation.dependencies.rate_limit import get_limiter

router = APIRouter()
settings = get_settings()
limiter = get_limiter()


@router.get(
    "/setup-check",
    response_model=FirstAdminCheckResponse,
    summary="Verificar Status do Sistema",
    description="Verifica o status do sistema (sempre permite criar novos administradores autorizados)",
)
async def check_setup(
    auth_service: AuthService = Depends(get_auth_service),
) -> FirstAdminCheckResponse:
    """Check system status for admin registration."""
    return await auth_service.check_first_admin_setup()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Administrador",
    description="Registra um novo usuário administrador do sistema (apenas emails autorizados)",
)
async def register_admin(
    user_data: UserCreateRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new admin user."""
    try:
        return await auth_service.register_first_admin(user_data)
    except DomainException as e:
        error_message = str(e)
        # Check if it's an authorization error
        if "ADMIN_NOT_AUTHORIZED" in error_message:
            # Remove the error code prefix for user-friendly message
            clean_message = error_message.replace("ADMIN_NOT_AUTHORIZED: ", "")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=clean_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
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
            max_age=settings.access_token_expire_minutes
            * 60,  # Convert to seconds
            expires=token_response.expires_at,
            httponly=True,
            secure=settings.is_production,  # Only HTTPS in production
            samesite="lax",
            path="/",
        )

        return token_response

    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logout de Usuário",
    description="Remove cookie de autenticação e revoga refresh token (AE-045)",
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    """Logout user by clearing auth cookie and revoking refresh token."""
    try:
        # Revoke refresh token in database
        await auth_service.logout(current_user.id)
        
        # Clear authentication cookie
        response.delete_cookie(
            key="access_token",
            path="/",
            secure=settings.is_production,
            httponly=True,
            samesite="lax",
        )
        
        # Clear refresh token cookie if it exists
        response.delete_cookie(
            key="refresh_token",
            path="/",
            secure=settings.is_production,
            httponly=True,
            samesite="lax",
        )

        return SuccessResponse(
            success=True, message="Logout realizado com sucesso"
        )
    except Exception:
        # Even if revocation fails, still clear cookies
        response.delete_cookie(
            key="access_token",
            path="/",
            secure=settings.is_production,
            httponly=True,
            samesite="lax",
        )
        response.delete_cookie(
            key="refresh_token",
            path="/",
            secure=settings.is_production,
            httponly=True,
            samesite="lax",
        )
        
        return SuccessResponse(
            success=True, message="Logout realizado com sucesso"
        )


@router.post(
    "/public-register",
    response_model=UserEnhancedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro Público",
    description="Auto-cadastro de usuário (cria com status PENDENTE aguardando aprovação)",
)
async def public_register(
    user_data: PublicUserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEnhancedResponse:
    """Public user registration (creates with PENDENTE status)."""
    try:
        return await auth_service.register_public_user(user_data)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/verify-email/{token}",
    response_model=SuccessResponse,
    summary="Verificar Email",
    description="Verifica o email do usuário usando o token enviado",
)
@limiter.limit("10/hour")
async def verify_email(
    request: Request,
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    """Verify user email with token."""
    try:
        success = await auth_service.verify_email(token)
        if success:
            return SuccessResponse(
                success=True, 
                message="Email verificado com sucesso! Você já pode fazer login."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível verificar o email"
            )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/resend-verification",
    response_model=SuccessResponse,
    summary="Reenviar Verificação",
    description="Reenvia email de verificação para o usuário",
)
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    """Resend email verification."""
    # TODO: Implement resend verification logic
    return SuccessResponse(
        success=True,
        message=f"Email de verificação reenviado para {request.email} (mock - implementar lógica real)"
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar Token",
    description="Renova o access token usando o refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    try:
        return await auth_service.refresh_access_token(request)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
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
        error_message = str(e)
        # Check if it's an authorization error
        if "ADMIN_NOT_AUTHORIZED" in error_message:
            # Remove the error code prefix for user-friendly message
            clean_message = error_message.replace("ADMIN_NOT_AUTHORIZED: ", "")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=clean_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Listar Usuários",
    description="Lista todos os usuários com paginação e filtros opcionais (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def list_users(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    role: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserListResponse:
    """List all users with pagination and optional filters (admin only)."""
    try:
        # If filters are provided, use filtered methods
        if status or role:
            from src.domain.enums import UserStatus, UserRole
            
            # Validate and use status filter
            if status:
                try:
                    status_enum = UserStatus(status)
                    return await auth_service.list_users_by_status(status_enum, limit, offset)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Status inválido: {status}. Use: PENDENTE, APROVADO, REJEITADO, SUSPENSO, INATIVO"
                    )
            
            # Validate and use role filter
            if role:
                try:
                    role_enum = UserRole(role)
                    return await auth_service.list_users_by_role(role_enum, limit, offset)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Role inválida: {role}. Use: admin, motorista, coletor, colaborador"
                    )
        
        # No filters, return all users
        request = UserListRequest(limit=limit, offset=offset)
        return await auth_service.list_users(request)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Atualizar Usuário",
    description="Atualiza dados do usuário (apenas admin)",
    dependencies=[Depends(get_current_admin_user)],
)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update user information (admin only)."""
    try:
        return await auth_service.update_user(user_id, user_data, current_user)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/users/{user_id}",
    summary="Excluir Usuário",
    description="Desativa usuário (soft delete) - apenas admin",
    dependencies=[Depends(get_current_admin_user)],
)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    """Soft delete user (admin only)."""
    try:
        success = await auth_service.delete_user(user_id, current_user)
        return {
            "success": success,
            "message": "Usuário excluído com sucesso",
        }
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
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
        },
    }
