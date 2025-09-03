"""
Authentication service for user management and JWT operations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

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
)
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.domain.repositories.user_repository_interface import (
    UserRepositoryInterface,
)
from src.infrastructure.config import Settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service handling user authentication and JWT operations.

    This service provides methods for user registration, login, token generation,
    and password management.
    """

    def __init__(
        self, user_repository: UserRepositoryInterface, settings: Settings
    ):
        """
        Initialize authentication service.

        Args:
            user_repository: User repository for data access
            settings: Application settings
        """
        self.user_repository = user_repository
        self.settings = settings

    async def check_first_admin_setup(self) -> FirstAdminCheckResponse:
        """
        Check system status for admin registration.
        Always allows new admin registration for authorized emails.

        Returns:
            FirstAdminCheckResponse: Setup status (always needs_setup=True)
        """
        has_admin = await self.user_repository.has_admin_users()

        return FirstAdminCheckResponse(
            needs_setup=True,  # Always allow new admin registration
            message=(
                "Sistema permite criar novos administradores autorizados"
                if has_admin
                else "Sistema precisa de configuração inicial de administrador"
            ),
        )

    async def register_first_admin(
        self, request: UserCreateRequest
    ) -> UserResponse:
        """
        Register an admin user in the system.

        Args:
            request: Admin user creation data

        Returns:
            UserResponse: Created admin user data

        Raises:
            DomainException: If creation fails or user not authorized
        """
        # Validate email against admin whitelist
        if not self._is_email_in_admin_whitelist(request.email):
            raise DomainException(
                "ADMIN_NOT_AUTHORIZED: O email fornecido não está autorizado para criar contas administrativas. "
                "Para solicitar acesso, entre em contato com o administrador do sistema ou com o suporte técnico."
            )

        # Ensure user is admin
        if not request.is_admin:
            request.is_admin = True

        return await self._create_user(request)

    async def register_user(self, request: UserCreateRequest) -> UserResponse:
        """
        Register a new user in the system.

        Args:
            request: User creation data

        Returns:
            UserResponse: Created user data

        Raises:
            DomainException: If user creation fails
        """
        # Validate admin email against whitelist if creating admin user
        if request.is_admin and not self._is_email_in_admin_whitelist(
            request.email
        ):
            raise DomainException(
                "ADMIN_NOT_AUTHORIZED: O email fornecido não está autorizado para criar contas administrativas. "
                "Para solicitar acesso, entre em contato com o administrador do sistema ou com o suporte técnico."
            )

        return await self._create_user(request)

    async def authenticate_user(self, request: LoginRequest) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            request: Login credentials

        Returns:
            User entity if authentication successful, None otherwise
        """
        user = await self.user_repository.get_by_email(request.email)

        if not user or not user.is_active:
            return None

        if not self.verify_password(request.password, user.password_hash):
            return None

        return user

    async def login(self, request: LoginRequest) -> TokenResponse:
        """
        Login user and generate JWT token.

        Args:
            request: Login credentials

        Returns:
            TokenResponse: JWT token and user data

        Raises:
            DomainException: If login fails
        """
        user = await self.authenticate_user(request)

        if not user:
            raise DomainException("Email ou senha incorretos")

        # Generate access token
        access_token, expires_at = self._create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            user=self._user_to_response(user),
        )

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            User entity if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm],
            )

            user_id: str = payload.get("sub")
            if not user_id:
                return None

        except InvalidTokenError:
            return None

        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None

        return user

    async def get_user_profile(self, user_id: str) -> AuthStatusResponse:
        """
        Get user profile information.

        Args:
            user_id: User unique identifier

        Returns:
            AuthStatusResponse: User profile data
        """
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            return AuthStatusResponse(
                success=False, message="Usuário não encontrado", user=None
            )

        return AuthStatusResponse(
            success=True,
            message="Perfil do usuário carregado com sucesso",
            user=self._user_to_response(user),
        )

    async def list_users(self, request: UserListRequest) -> UserListResponse:
        """
        List all users with pagination (admin only).

        Args:
            request: Pagination parameters

        Returns:
            UserListResponse: Paginated list of users
        """
        users = await self.user_repository.list_users(
            limit=request.limit, offset=request.offset
        )
        total = await self.user_repository.count_total_users()
        
        has_next = (request.offset + request.limit) < total

        return UserListResponse(
            users=[self._user_to_response(user) for user in users],
            total=total,
            limit=request.limit,
            offset=request.offset,
            has_next=has_next,
        )

    async def update_user(
        self, user_id: str, request: UserUpdateRequest, current_user: User
    ) -> UserResponse:
        """
        Update user information (admin only).

        Args:
            user_id: User ID to update
            request: Update data
            current_user: User making the request

        Returns:
            UserResponse: Updated user data

        Raises:
            DomainException: If update fails or validation errors
        """
        # Get user to update
        user_to_update = await self.user_repository.get_by_id(user_id)
        if not user_to_update:
            raise DomainException("Usuário não encontrado")

        # Prevent user from deactivating themselves
        if user_id == current_user.id and request.is_active is False:
            raise DomainException(
                "Você não pode desativar sua própria conta"
            )

        # Prevent removing admin from themselves
        if user_id == current_user.id and request.is_admin is False:
            raise DomainException(
                "Você não pode remover seus próprios privilégios de administrador"
            )

        # Check if trying to deactivate or remove admin privileges from last admin
        if (request.is_active is False or request.is_admin is False) and user_to_update.is_admin:
            await self._ensure_not_last_admin(user_id)

        # Update user fields
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.is_admin is not None:
            update_data["is_admin"] = request.is_admin
        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        # Create updated user entity
        updated_user = User(
            id=user_to_update.id,
            email=user_to_update.email,
            name=update_data.get("name", user_to_update.name),
            password_hash=user_to_update.password_hash,
            is_admin=update_data.get("is_admin", user_to_update.is_admin),
            is_active=update_data.get("is_active", user_to_update.is_active),
            created_at=user_to_update.created_at,
        )

        # Save updated user
        result = await self.user_repository.update(user_id, updated_user)
        if not result:
            raise DomainException("Erro ao atualizar usuário")

        return self._user_to_response(result)

    async def delete_user(self, user_id: str, current_user: User) -> bool:
        """
        Soft delete user (admin only).

        Args:
            user_id: User ID to delete
            current_user: User making the request

        Returns:
            True if user was deleted successfully

        Raises:
            DomainException: If deletion fails or validation errors
        """
        # Get user to delete
        user_to_delete = await self.user_repository.get_by_id(user_id)
        if not user_to_delete:
            raise DomainException("Usuário não encontrado")

        # Prevent user from deleting themselves
        if user_id == current_user.id:
            raise DomainException("Você não pode excluir sua própria conta")

        # Check if trying to delete last admin
        if user_to_delete.is_admin:
            await self._ensure_not_last_admin(user_id)

        # Soft delete user
        success = await self.user_repository.soft_delete(user_id)
        if not success:
            raise DomainException("Erro ao excluir usuário")

        return True

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def _is_email_in_admin_whitelist(self, email: str) -> bool:
        """
        Check if email is authorized to create admin accounts.

        Args:
            email: Email address to validate

        Returns:
            True if email is in whitelist or whitelist is disabled, False otherwise
        """
        # If no whitelist is configured, allow all emails (backward compatibility)
        if not self.settings.admin_email_whitelist:
            return True

        # Normalize email for comparison
        normalized_email = email.lower().strip()

        # Check if email is in whitelist
        return normalized_email in self.settings.admin_email_whitelist

    def _create_access_token(self, user: User) -> tuple[str, datetime]:
        """
        Create JWT access token for user.

        Args:
            user: User entity

        Returns:
            Tuple of (token, expiration_datetime)
        """
        expires_delta = timedelta(
            minutes=self.settings.access_token_expire_minutes
        )
        expires_at = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "sub": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "exp": expires_at,
            "iat": datetime.now(timezone.utc),
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )

        return encoded_jwt, expires_at

    async def _create_user(self, request: UserCreateRequest) -> UserResponse:
        """
        Create new user with validation.

        Args:
            request: User creation data

        Returns:
            UserResponse: Created user data

        Raises:
            DomainException: If user creation fails
        """
        # Check if user already exists
        if await self.user_repository.exists_by_email(request.email):
            raise DomainException(
                f"Usuário com email '{request.email}' já existe"
            )

        # Create user entity
        user = User(
            email=request.email,
            name=request.name,
            password_hash=self.hash_password(request.password),
            is_admin=request.is_admin,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        # Save user
        created_user = await self.user_repository.create(user)

        return self._user_to_response(created_user)

    async def _ensure_not_last_admin(self, user_id: str) -> None:
        """
        Ensure we're not removing the last admin from the system.

        Args:
            user_id: ID of the user being modified

        Raises:
            DomainException: If this would remove the last admin
        """
        # Count active admins excluding the current user
        total_admins = 0
        try:
            # Get all active admin users
            all_users = await self.user_repository.list_users(limit=1000, offset=0)
            active_admins = [
                user for user in all_users 
                if user.is_admin and user.is_active and user.id != user_id
            ]
            total_admins = len(active_admins)
        except Exception:
            total_admins = 0

        if total_admins == 0:
            raise DomainException(
                "Não é possível remover o último administrador do sistema. "
                "Deve haver pelo menos um administrador ativo."
            )

    def _user_to_response(self, user: User) -> UserResponse:
        """
        Convert User entity to UserResponse DTO.

        Args:
            user: User entity

        Returns:
            UserResponse: User response DTO
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
        )
