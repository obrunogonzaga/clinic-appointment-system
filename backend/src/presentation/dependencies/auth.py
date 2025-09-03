"""
Authentication dependencies for FastAPI route protection.
"""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.container import get_app_settings, get_user_repository
from src.infrastructure.repositories.user_repository import UserRepository

# HTTP Bearer token scheme (for API documentation)
security = HTTPBearer(auto_error=False)


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    settings=Depends(get_app_settings),
) -> AuthService:
    """
    Dependency to get authentication service instance.

    Returns:
        AuthService: Authentication service
    """
    return AuthService(user_repository, settings)


async def get_token_from_cookie_or_header(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """
    Get JWT token from either cookie or Authorization header.

    Priority: Cookie first, then Authorization header

    Args:
        access_token: Token from httpOnly cookie
        authorization: Token from Authorization header

    Returns:
        JWT token string if present, None otherwise
    """
    # First try cookie (primary method for web app)
    if access_token:
        return access_token

    # Then try Authorization header (for API clients)
    if authorization:
        return authorization.credentials

    return None


async def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    token: Optional[str] = Depends(get_token_from_cookie_or_header),
) -> User:
    """
    Get current authenticated user from JWT token.

    This dependency requires authentication and will raise HTTP 401
    if no valid token is provided.

    Args:
        auth_service: Authentication service
        token: JWT token

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    user = await auth_service.get_current_user(token)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (wrapper for clarity).

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current admin user.

    This dependency requires the user to be both authenticated and admin.

    Args:
        current_user: Current user from get_current_active_user

    Returns:
        User: Current admin user

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.has_admin_privileges():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: privilégios de administrador necessários",
        )
    return current_user


async def get_current_user_optional(
    auth_service: AuthService = Depends(get_auth_service),
    token: Optional[str] = Depends(get_token_from_cookie_or_header),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

    This dependency is optional and won't raise exceptions for
    unauthenticated users.

    Args:
        auth_service: Authentication service
        token: JWT token

    Returns:
        User if authenticated, None otherwise
    """
    if not token:
        return None

    user = await auth_service.get_current_user(token)
    return user if user and user.is_active else None
