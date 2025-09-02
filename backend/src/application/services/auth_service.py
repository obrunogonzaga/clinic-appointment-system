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
)
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.domain.repositories.user_repository_interface import UserRepositoryInterface
from src.infrastructure.config import Settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service handling user authentication and JWT operations.
    
    This service provides methods for user registration, login, token generation,
    and password management.
    """

    def __init__(self, user_repository: UserRepositoryInterface, settings: Settings):
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
        Check if the system needs initial admin setup.
        
        Returns:
            FirstAdminCheckResponse: Setup status
        """
        has_admin = await self.user_repository.has_admin_users()
        
        return FirstAdminCheckResponse(
            needs_setup=not has_admin,
            message="Sistema precisa de configuração inicial de administrador" 
                    if not has_admin 
                    else "Sistema já possui administrador configurado"
        )

    async def register_first_admin(self, request: UserCreateRequest) -> UserResponse:
        """
        Register the first admin user in the system.
        
        Args:
            request: Admin user creation data
            
        Returns:
            UserResponse: Created admin user data
            
        Raises:
            DomainException: If admin already exists or creation fails
        """
        # Check if admin already exists
        if await self.user_repository.has_admin_users():
            raise DomainException("Sistema já possui administrador configurado")

        # Ensure first user is admin
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
            user=self._user_to_response(user)
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
                algorithms=[self.settings.algorithm]
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
                success=False,
                message="Usuário não encontrado",
                user=None
            )

        return AuthStatusResponse(
            success=True,
            message="Perfil do usuário carregado com sucesso",
            user=self._user_to_response(user)
        )

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, user: User) -> tuple[str, datetime]:
        """
        Create JWT access token for user.
        
        Args:
            user: User entity
            
        Returns:
            Tuple of (token, expiration_datetime)
        """
        expires_delta = timedelta(minutes=self.settings.access_token_expire_minutes)
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
            algorithm=self.settings.algorithm
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
            raise DomainException(f"Usuário com email '{request.email}' já existe")

        # Create user entity
        user = User(
            email=request.email,
            name=request.name,
            password_hash=self.hash_password(request.password),
            is_admin=request.is_admin,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        # Save user
        created_user = await self.user_repository.create(user)
        
        return self._user_to_response(created_user)

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
            created_at=user.created_at
        )