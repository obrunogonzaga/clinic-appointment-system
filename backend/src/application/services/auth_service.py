"""
Authentication service for user management and JWT operations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List

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
    PublicUserRegisterRequest,
    UserEnhancedResponse,
    PendingUsersResponse,
    UserApprovalRequest,
    UserRejectionRequest,
    DashboardStatsResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from src.application.services.notification_manager_service import NotificationManagerService
from src.domain.base import DomainException
from src.domain.entities.user import User
from src.domain.entities.user_enhanced import UserEnhanced
from src.domain.enums import UserStatus, UserRole
from src.domain.repositories.user_repository_interface import (
    UserRepositoryInterface,
)
from src.domain.services.token_service import TokenService
from src.infrastructure.config import Settings
from src.infrastructure.services.email_service import EmailService
from src.infrastructure.services.redis_service import RedisService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service handling user authentication and JWT operations.

    This service provides methods for user registration, login, token generation,
    and password management.
    """

    def __init__(
        self, 
        user_repository: UserRepositoryInterface, 
        settings: Settings,
        notification_manager: Optional[NotificationManagerService] = None
    ):
        """
        Initialize authentication service.

        Args:
            user_repository: User repository for data access
            settings: Application settings
            notification_manager: Optional notification manager service
        """
        self.user_repository = user_repository
        self.settings = settings
        self.notification_manager = notification_manager
        self.email_service = EmailService(settings)
        self.token_service = TokenService(settings)
        self.redis_service = None  # Will be injected if available

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
        Authenticate user with email and password with security checks.

        Args:
            request: Login credentials

        Returns:
            User entity if authentication successful, None otherwise
            
        Raises:
            DomainException: For specific authentication failures
        """
        user = await self.user_repository.get_by_email(request.email)

        if not user:
            return None
        
        # Check if user is enhanced (has status field)
        if isinstance(user, UserEnhanced):
            security = user.security

            # Check if account is locked due to failed attempts
            locked_until = security.account_locked_until
            if locked_until:
                if isinstance(locked_until, datetime) and locked_until > datetime.utcnow():
                    remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60)
                    raise DomainException(
                        "Conta bloqueada por muitas tentativas falhas. "
                        f"Tente novamente em {remaining_minutes} minutos."
                    )
                else:
                    # Lock expired, reset it
                    security.account_locked_until = None
                    security.failed_login_attempts = 0
            
            # Check if user is approved
            if user.status != UserStatus.APROVADO:
                if user.status == UserStatus.PENDENTE:
                    raise DomainException("Sua conta ainda está aguardando aprovação do administrador")
                elif user.status == UserStatus.REJEITADO:
                    raise DomainException("Sua conta foi rejeitada. Entre em contato com o administrador")
                elif user.status == UserStatus.SUSPENSO:
                    raise DomainException("Sua conta está suspensa. Entre em contato com o administrador")
                else:
                    raise DomainException("Sua conta não está ativa")
            
            # Check if email is verified (make it mandatory)
            if not security.email_verified:
                raise DomainException("Por favor, verifique seu email antes de fazer login")
        else:
            # Legacy user check (backward compatibility)
            if not user.is_active:
                return None

        # Verify password
        password_valid = self.verify_password(request.password, user.password_hash)
        
        if isinstance(user, UserEnhanced):
            security = user.security
            if not password_valid:
                # Increment failed attempts
                failed_attempts = (security.failed_login_attempts or 0) + 1
                security.failed_login_attempts = failed_attempts
                security.last_failed_attempt = datetime.utcnow()
                
                # Lock account if max attempts reached
                if failed_attempts >= self.settings.max_login_attempts:
                    lock_until = datetime.utcnow() + timedelta(minutes=self.settings.account_lock_minutes)
                    security.account_locked_until = lock_until
                    
                    # Update user in database
                    await self.user_repository.update(user.id, user)
                    
                    # Send email notification about account lock
                    await self.email_service.send_account_locked_email(
                        user, failed_attempts
                    )
                    
                    raise DomainException(
                        f"Conta bloqueada após {failed_attempts} tentativas falhas. "
                        f"Tente novamente em {self.settings.account_lock_minutes} minutos."
                    )
                else:
                    # Update failed attempts in database
                    await self.user_repository.update(user.id, user)
                    return None
            else:
                # Reset failed attempts on successful password verification
                if (security.failed_login_attempts or 0) > 0:
                    security.failed_login_attempts = 0
                    security.last_successful_login = datetime.utcnow()
                    await self.user_repository.update(user.id, user)
        else:
            if not password_valid:
                return None

        return user

    async def login(self, request: LoginRequest) -> TokenResponse:
        """
        Login user and generate JWT and refresh tokens.

        Args:
            request: Login credentials

        Returns:
            TokenResponse: JWT token, refresh token and user data

        Raises:
            DomainException: If login fails
        """
        user = await self.authenticate_user(request)

        if not user:
            raise DomainException("Email ou senha incorretos")

        # Generate access token using TokenService
        access_token, expires_at = self.token_service.create_access_token(
            user_id=user.id,
            user_email=user.email,
            is_admin=user.is_admin if hasattr(user, 'is_admin') else False,
            additional_claims={
                "role": self._resolve_role_claim(user)
            }
        )
        
        # Generate refresh token for enhanced users
        refresh_token = None
        if isinstance(user, UserEnhanced):
            refresh_token_data = self.token_service.create_refresh_token(
                user_id=user.id,
                token_family=user.security.refresh_token_family
            )
            refresh_token = refresh_token_data[0]
            refresh_expires = refresh_token_data[1]
            family_id = refresh_token_data[2]
            
            # Store hashed refresh token in user
            hashed_refresh = self.token_service._hash_token(refresh_token)
            user.security.refresh_token = hashed_refresh
            user.security.refresh_token_expires = refresh_expires
            user.security.refresh_token_family = family_id
            
            # Update user in database
            await self.user_repository.update(user.id, user)

        # Create response with proper user type
        response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            user=self._user_to_response(user),
        )
        
        # Add refresh token to response if available
        if refresh_token:
            response.refresh_token = refresh_token
            
        return response

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

        # Return enhanced response if user is UserEnhanced
        if isinstance(user, UserEnhanced):
            return AuthStatusResponse(
                success=True,
                message="Perfil do usuário carregado com sucesso",
                user=self._user_to_enhanced_response(user),
            )
        else:
            # Legacy response for backward compatibility
            return AuthStatusResponse(
                success=True,
                message="Perfil do usuário carregado com sucesso",
                user=self._user_to_response(user),
            )

    async def list_users_by_status(
        self, status: UserStatus, limit: int = 10, offset: int = 0
    ) -> UserListResponse:
        """
        List users filtered by status.
        
        Args:
            status: User status to filter by
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            UserListResponse: Filtered list of users
        """
        users = await self.user_repository.get_users_by_status(status, limit, offset)
        total = await self.user_repository.count_users_by_status(status)
        
        has_next = (offset + limit) < total
        
        # Convert to appropriate response type
        response_users = []
        for user in users:
            if isinstance(user, UserEnhanced):
                response_users.append(self._user_to_enhanced_response(user))
            else:
                response_users.append(self._user_to_response(user))
        
        return UserListResponse(
            users=response_users,
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
        )
    
    async def list_users_by_role(
        self, role: UserRole, limit: int = 10, offset: int = 0
    ) -> UserListResponse:
        """
        List users filtered by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            UserListResponse: Filtered list of users
        """
        users = await self.user_repository.get_users_by_role(role, limit, offset)
        
        # Count users with this role
        total = len(await self.user_repository.get_users_by_role(role, limit=1000, offset=0))
        
        has_next = (offset + limit) < total
        
        # Convert to appropriate response type
        response_users = []
        for user in users:
            if isinstance(user, UserEnhanced):
                response_users.append(self._user_to_enhanced_response(user))
            else:
                response_users.append(self._user_to_response(user))
        
        return UserListResponse(
            users=response_users,
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
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

    def _resolve_role_claim(self, user: User) -> str:
        """Resolve role claim for JWT payload handling legacy values."""
        default_role = "admin" if getattr(user, "is_admin", False) else "colaborador"

        if isinstance(user, UserEnhanced):
            role_value = getattr(user, "role", None)
            if hasattr(role_value, "value"):
                return role_value.value
            if isinstance(role_value, str) and role_value:
                return role_value

        return default_role

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
    
    def _user_to_enhanced_response(self, user: UserEnhanced) -> UserEnhancedResponse:
        """
        Convert UserEnhanced entity to UserEnhancedResponse DTO.
        
        Args:
            user: UserEnhanced entity
            
        Returns:
            UserEnhancedResponse: Enhanced user response DTO
        """
        return UserEnhancedResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            status=user.status,
            phone=user.metadata.phone,
            department=user.metadata.department,
            email_verified=user.security.email_verified,
            created_at=user.created_at,
            created_by=user.created_by,
            approved_by=user.approval.approved_by,
            approved_at=user.approval.approved_at,
            rejected_by=user.approval.rejected_by,
            rejected_at=user.approval.rejected_at,
            rejection_reason=user.approval.rejection_reason,
        )
    
    async def register_public_user(
        self, request: PublicUserRegisterRequest
    ) -> UserEnhancedResponse:
        """
        Register a new user through public registration (self-service).
        Creates user with PENDENTE status awaiting admin approval.
        
        Args:
            request: Public registration data
            
        Returns:
            UserEnhancedResponse: Created user data
            
        Raises:
            DomainException: If registration fails
        """
        # Check if user already exists
        if await self.user_repository.exists_by_email(request.email):
            raise DomainException(
                f"Usuário com email '{request.email}' já existe"
            )
        
        # Create UserEnhanced entity with PENDENTE status
        user = UserEnhanced(
            email=request.email,
            name=request.name,
            password_hash=self.hash_password(request.password),
            role=request.role,
            status=UserStatus.PENDENTE,
            created_at=datetime.now(timezone.utc),
            created_by=None,  # Self-registered
        )

        # Populate metadata/security using model fields to avoid dict mutation issues
        user.metadata.phone = request.phone
        user.metadata.cpf = request.cpf
        user.metadata.department = request.department
        if request.role == UserRole.MOTORISTA:
            user.metadata.drivers_license = request.drivers_license

        user.security.email_verified = False  # Requires verification
        
        # Generate email verification token using TokenService
        token, hashed_token, expires_at = self.token_service.generate_email_verification_token()
        
        # Update user with verification token
        user.security.email_verification_token = hashed_token
        user.security.email_verification_expires = expires_at
        
        # Save user
        created_user = await self.user_repository.create(user)
        
        # Send email verification using real EmailService
        await self.email_service.send_verification_email(
            created_user, token  # Send plain token to user
        )
        
        # Create notification for pending user approval (if notification manager available)
        if self.notification_manager:
            await self.notification_manager.create_user_pending_notification(
                created_user
            )
        
        # Send email to admins
        # Get admin emails from settings (from whitelist)
        admin_emails = self.settings.admin_email_whitelist if hasattr(self.settings, 'admin_email_whitelist') else []
        if admin_emails:
            await self.email_service.send_admin_notification(
                created_user, admin_emails
            )
        
        return self._user_to_enhanced_response(created_user)
    
    async def refresh_access_token(
        self, request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            request: Refresh token request
            
        Returns:
            RefreshTokenResponse: New tokens
            
        Raises:
            DomainException: If refresh fails
        """
        # Verify refresh token
        claims = self.token_service.verify_refresh_token(request.refresh_token)
        if not claims:
            raise DomainException("Token de atualização inválido ou expirado")
        
        user_id = claims.get("sub")
        if not user_id:
            raise DomainException("Token de atualização inválido")
        
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise DomainException("Usuário não encontrado")
        
        # Check if user is enhanced and has refresh token
        if isinstance(user, UserEnhanced):
            stored_refresh = user.security.refresh_token
            if not stored_refresh:
                raise DomainException("Token de atualização não encontrado")
            
            # Verify token matches stored hash
            token_hash = self.token_service._hash_token(request.refresh_token)
            if token_hash != stored_refresh:
                # Possible token theft - invalidate all tokens
                user.security.refresh_token = None
                user.security.refresh_token_expires = None
                user.security.refresh_token_family = None
                await self.user_repository.update(user.id, user)
                raise DomainException("Token de atualização inválido - possível comprometimento")
            
            # Generate new access token
            access_token, expires_at = self.token_service.create_access_token(
                user_id=user.id,
                user_email=user.email,
                is_admin=user.is_admin if hasattr(user, 'is_admin') else False,
                additional_claims={
                    "role": self._resolve_role_claim(user)
                }
            )
            
            # Rotate refresh token (best practice)
            new_refresh_data = self.token_service.rotate_refresh_token(
                request.refresh_token, user.id
            )
            
            if new_refresh_data:
                new_refresh_token = new_refresh_data[0]
                refresh_expires = new_refresh_data[1]
                family_id = new_refresh_data[2]
                
                # Update stored refresh token
                hashed_refresh = self.token_service._hash_token(new_refresh_token)
                user.security.refresh_token = hashed_refresh
                user.security.refresh_token_expires = refresh_expires
                user.security.refresh_token_family = family_id
                await self.user_repository.update(user.id, user)
                
                return RefreshTokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    expires_at=expires_at,
                    refresh_token=new_refresh_token,
                    refresh_expires_at=refresh_expires
                )
        
        raise DomainException("Token de atualização não suportado para usuário legado")
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email with token.
        
        Args:
            token: Verification token
            
        Returns:
            True if verified successfully
            
        Raises:
            DomainException: If verification fails
        """
        # Find user by token
        user = await self.user_repository.get_by_email_verification_token(token)
        if not user:
            raise DomainException("Token de verificação inválido ou expirado")
        
        if isinstance(user, UserEnhanced):
            # Verify token hasn't expired
            expires = user.security.email_verification_expires
            if expires and expires < datetime.utcnow():
                raise DomainException("Token de verificação expirado")
            
            # Verify token hash matches
            stored_hash = user.security.email_verification_token
            if not stored_hash:
                raise DomainException("Token de verificação não encontrado")
            
            if not self.token_service.verify_email_token(
                token, stored_hash, expires
            ):
                raise DomainException("Token de verificação inválido")
            
            # Mark email as verified
            user.security.email_verified = True
            user.security.email_verified_at = datetime.utcnow()
            user.security.email_verification_token = None
            user.security.email_verification_expires = None
            
            await self.user_repository.update(user.id, user)
            return True
        
        raise DomainException("Verificação não suportada para usuário legado")
    
    async def get_pending_users(
        self, limit: int = 10, offset: int = 0
    ) -> PendingUsersResponse:
        """
        Get list of users pending approval.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            PendingUsersResponse: List of pending users
        """
        users = await self.user_repository.get_pending_users(limit, offset)
        total = await self.user_repository.count_pending_users()
        
        has_next = (offset + limit) < total
        
        enhanced_users = []
        for user in users:
            if isinstance(user, UserEnhanced):
                enhanced_users.append(self._user_to_enhanced_response(user))
        
        return PendingUsersResponse(
            users=enhanced_users,
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
        )
    
    async def approve_user(
        self, user_id: str, admin_user: User, request: UserApprovalRequest
    ) -> UserEnhancedResponse:
        """
        Approve a pending user.
        
        Args:
            user_id: ID of user to approve
            admin_user: Admin performing the approval
            request: Approval request data
            
        Returns:
            UserEnhancedResponse: Approved user data
            
        Raises:
            DomainException: If approval fails
        """
        # Approve user in repository
        approved_user = await self.user_repository.approve_user(
            user_id, admin_user.id
        )
        
        if not approved_user:
            raise DomainException("Usuário não encontrado ou já foi processado")
        
        # Send approval notification to user
        if isinstance(approved_user, UserEnhanced):
            # Send email notification
            await self.email_service.send_welcome_email(approved_user)
            
            # Create in-app notification if notification manager available
            if self.notification_manager:
                from src.application.dtos.notification_dto import CreateNotificationRequest
                from src.domain.entities.notification import NotificationType, NotificationPriority
                
                notification_request = CreateNotificationRequest(
                    type=NotificationType.USER_APPROVED,
                    title="Conta Aprovada",
                    message=f"Sua conta foi aprovada por {admin_user.name}. Você já pode fazer login no sistema.",
                    user_id=approved_user.id,
                    source_user_id=admin_user.id,
                    priority=NotificationPriority.MEDIUM,
                    action_url="/login",
                    data={
                        "approved_by": admin_user.name,
                        "approved_at": datetime.utcnow().isoformat()
                    }
                )
                await self.notification_manager.create_notification(notification_request)
            
            return self._user_to_enhanced_response(approved_user)
        
        raise DomainException("Erro ao aprovar usuário")
    
    async def reject_user(
        self, user_id: str, admin_user: User, request: UserRejectionRequest
    ) -> UserEnhancedResponse:
        """
        Reject a pending user.
        
        Args:
            user_id: ID of user to reject
            admin_user: Admin performing the rejection
            request: Rejection request data
            
        Returns:
            UserEnhancedResponse: Rejected user data
            
        Raises:
            DomainException: If rejection fails
        """
        # Reject user in repository
        rejected_user = await self.user_repository.reject_user(
            user_id, admin_user.id, request.reason
        )
        
        if not rejected_user:
            raise DomainException("Usuário não encontrado ou já foi processado")
        
        # Send rejection notification to user
        if isinstance(rejected_user, UserEnhanced):
            # Send email notification
            await self.email_service.send_rejection_email(
                rejected_user, request.reason
            )
            
            # Create in-app notification if notification manager available
            if self.notification_manager:
                from src.application.dtos.notification_dto import CreateNotificationRequest
                from src.domain.entities.notification import NotificationType, NotificationPriority
                
                notification_request = CreateNotificationRequest(
                    type=NotificationType.USER_REJECTED,
                    title="Solicitação Rejeitada",
                    message=f"Sua solicitação de cadastro foi rejeitada. Motivo: {request.reason}",
                    user_id=rejected_user.id,
                    source_user_id=admin_user.id,
                    priority=NotificationPriority.HIGH,
                    data={
                        "rejected_by": admin_user.name,
                        "rejected_at": datetime.utcnow().isoformat(),
                        "reason": request.reason
                    }
                )
                await self.notification_manager.create_notification(notification_request)
            
            return self._user_to_enhanced_response(rejected_user)
        
        raise DomainException("Erro ao rejeitar usuário")
    
    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """
        Get dashboard statistics for admin.
        
        Returns:
            DashboardStatsResponse: Dashboard statistics
        """
        # Get counts by status
        total_users = await self.user_repository.count_total_users()
        pending_users = await self.user_repository.count_pending_users()
        approved_users = await self.user_repository.count_users_by_status(UserStatus.APROVADO)
        rejected_users = await self.user_repository.count_users_by_status(UserStatus.REJEITADO)
        suspended_users = await self.user_repository.count_users_by_status(UserStatus.SUSPENSO)
        
        # Get users by role
        users_by_role = {}
        for role in UserRole:
            count = 0
            role_users = await self.user_repository.get_users_by_role(role, limit=1000)
            users_by_role[role.value] = len(role_users)
        
        # Get recent registrations and pending approvals
        recent_users = await self.user_repository.list_users(limit=5, offset=0)
        pending_list = await self.user_repository.get_pending_users(limit=10, offset=0)
        
        recent_registrations = []
        for user in recent_users:
            if isinstance(user, UserEnhanced):
                recent_registrations.append(self._user_to_enhanced_response(user))
        
        pending_approvals = []
        for user in pending_list:
            if isinstance(user, UserEnhanced):
                pending_approvals.append(self._user_to_enhanced_response(user))
        
        return DashboardStatsResponse(
            total_users=total_users,
            pending_users=pending_users,
            approved_users=approved_users,
            rejected_users=rejected_users,
            suspended_users=suspended_users,
            users_by_role=users_by_role,
            recent_registrations=recent_registrations,
            pending_approvals=pending_approvals,
        )
    
    async def logout(self, user_id: str) -> bool:
        """
        Logout user by revoking refresh token (AE-045).
        
        Args:
            user_id: User ID to logout
            
        Returns:
            bool: True if logout successful
        """
        try:
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False
            
            # Clear refresh token and related fields
            user.security.refresh_token = None
            user.security.refresh_token_expires = None
            user.security.refresh_token_family = None
            
            # Update user in database
            await self.user_repository.update(user_id, user)
            
            return True
            
        except Exception:
            # Don't throw error on logout failure
            return False
