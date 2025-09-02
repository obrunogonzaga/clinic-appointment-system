"""
Tests for authentication functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.application.services.auth_service import AuthService
from src.application.dtos.user_dto import UserCreateRequest, LoginRequest
from src.domain.entities.user import User
from src.domain.base import DomainException
from src.infrastructure.config import Settings


@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def auth_service(mock_user_repository):
    """Create auth service with mocked dependencies."""
    settings = Settings(
        secret_key="test-secret-key",
        access_token_expire_minutes=30,
        algorithm="HS256"
    )
    return AuthService(mock_user_repository, settings)


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id="507f1f77bcf86cd799439011",
        email="test@example.com",
        name="Test User",
        password_hash="$2b$12$hashed_password",
        is_admin=False,
        is_active=True,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def admin_user():
    """Sample admin user for testing."""
    return User(
        id="507f1f77bcf86cd799439012",
        email="admin@example.com",
        name="Admin User",
        password_hash="$2b$12$hashed_password",
        is_admin=True,
        is_active=True,
        created_at=datetime.utcnow()
    )


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.mark.asyncio
    async def test_check_first_admin_setup_needed(self, auth_service, mock_user_repository):
        """Test checking if first admin setup is needed."""
        # Setup
        mock_user_repository.has_admin_users.return_value = False
        
        # Execute
        result = await auth_service.check_first_admin_setup()
        
        # Assert
        assert result.needs_setup is True
        assert "configuração inicial" in result.message.lower()
        mock_user_repository.has_admin_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_first_admin_setup_not_needed(self, auth_service, mock_user_repository):
        """Test checking when admin already exists."""
        # Setup
        mock_user_repository.has_admin_users.return_value = True
        
        # Execute
        result = await auth_service.check_first_admin_setup()
        
        # Assert
        assert result.needs_setup is False
        assert "já possui administrador" in result.message.lower()

    @pytest.mark.asyncio
    async def test_register_first_admin_success(self, auth_service, mock_user_repository, admin_user):
        """Test successful first admin registration."""
        # Setup
        mock_user_repository.has_admin_users.return_value = False
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.create.return_value = admin_user
        
        request = UserCreateRequest(
            email="admin@example.com",
            name="Admin User",
            password="password123",
            is_admin=True
        )
        
        # Execute
        result = await auth_service.register_first_admin(request)
        
        # Assert
        assert result.email == "admin@example.com"
        assert result.name == "Admin User"
        assert result.is_admin is True
        mock_user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_first_admin_already_exists(self, auth_service, mock_user_repository):
        """Test first admin registration when admin already exists."""
        # Setup
        mock_user_repository.has_admin_users.return_value = True
        
        request = UserCreateRequest(
            email="admin@example.com",
            name="Admin User",
            password="password123",
            is_admin=True
        )
        
        # Execute & Assert
        with pytest.raises(DomainException, match="já possui administrador"):
            await auth_service.register_first_admin(request)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repository, sample_user):
        """Test successful user authentication."""
        # Setup
        mock_user_repository.get_by_email.return_value = sample_user
        # Mock password verification to return True
        auth_service.verify_password = MagicMock(return_value=True)
        
        request = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        # Execute
        result = await auth_service.authenticate_user(request)
        
        # Assert
        assert result is not None
        assert result.email == "test@example.com"
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, mock_user_repository, sample_user):
        """Test authentication with wrong password."""
        # Setup
        mock_user_repository.get_by_email.return_value = sample_user
        # Mock password verification to return False
        auth_service.verify_password = MagicMock(return_value=False)
        
        request = LoginRequest(
            email="test@example.com",
            password="wrong_password"
        )
        
        # Execute
        result = await auth_service.authenticate_user(request)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_user_repository):
        """Test authentication with non-existent user."""
        # Setup
        mock_user_repository.get_by_email.return_value = None
        
        request = LoginRequest(
            email="nonexistent@example.com",
            password="password123"
        )
        
        # Execute
        result = await auth_service.authenticate_user(request)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_repository, sample_user):
        """Test successful login."""
        # Setup
        mock_user_repository.get_by_email.return_value = sample_user
        auth_service.verify_password = MagicMock(return_value=True)
        
        request = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        # Execute
        result = await auth_service.login(request)
        
        # Assert
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_failure(self, auth_service, mock_user_repository):
        """Test login failure."""
        # Setup
        mock_user_repository.get_by_email.return_value = None
        
        request = LoginRequest(
            email="test@example.com",
            password="wrong_password"
        )
        
        # Execute & Assert
        with pytest.raises(DomainException, match="Email ou senha incorretos"):
            await auth_service.login(request)

    def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "test_password"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed) is True

    def test_verify_password(self, auth_service):
        """Test password verification."""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password(wrong_password, hashed) is False

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, auth_service, mock_user_repository, sample_user):
        """Test getting current user with valid token."""
        # Setup - create a real token first
        mock_user_repository.get_by_email.return_value = sample_user
        auth_service.verify_password = MagicMock(return_value=True)
        
        # Create token
        token_response = await auth_service.login(LoginRequest(
            email="test@example.com",
            password="password123"
        ))
        
        # Setup for get_by_id call
        mock_user_repository.get_by_id.return_value = sample_user
        
        # Execute
        result = await auth_service.get_current_user(token_response.access_token)
        
        # Assert
        assert result is not None
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, auth_service, mock_user_repository):
        """Test getting current user with invalid token."""
        # Execute
        result = await auth_service.get_current_user("invalid_token")
        
        # Assert
        assert result is None