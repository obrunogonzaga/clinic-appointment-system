"""
Notification service for sending emails and notifications.
"""

from typing import List, Optional
from datetime import datetime
import logging

from src.domain.entities.user_enhanced import UserEnhanced
from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for handling notifications (emails, SMS, etc).
    
    Currently implements mock notifications for development.
    Will be replaced with actual email service (SendGrid/SES) later.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize notification service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.mock_mode = True  # Using mock mode for now
        
    async def send_admin_new_user_notification(
        self, user: UserEnhanced, admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Notify admins about new user registration pending approval.
        
        Args:
            user: User who registered
            admin_emails: List of admin emails to notify
            
        Returns:
            True if notification sent successfully
        """
        if self.mock_mode:
            logger.info(
                f"[MOCK] Sending new user notification to admins for user: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Novo Cadastro Pendente - {user.name}"
            )
            logger.info(
                f"[MOCK] Body: Um novo usuário se cadastrou e aguarda aprovação.\n"
                f"Nome: {user.name}\n"
                f"Email: {user.email}\n"
                f"Role Solicitada: {user.role}\n"
                f"Data: {datetime.utcnow().isoformat()}"
            )
            return True
        
        # TODO: Implement actual email sending
        return False
    
    async def send_approval_notification(self, user: UserEnhanced) -> bool:
        """
        Send approval notification to user.
        
        Args:
            user: Approved user
            
        Returns:
            True if notification sent successfully
        """
        if self.mock_mode:
            logger.info(
                f"[MOCK] Sending approval notification to: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Cadastro Aprovado - Bem-vindo!"
            )
            logger.info(
                f"[MOCK] Body: Olá {user.name},\n\n"
                f"Seu cadastro foi aprovado! Você já pode acessar o sistema.\n"
                f"Role: {user.role}\n"
                f"Acesse: {self.settings.frontend_url}/login"
            )
            return True
        
        # TODO: Implement actual email sending
        return False
    
    async def send_rejection_notification(
        self, user: UserEnhanced, reason: str
    ) -> bool:
        """
        Send rejection notification to user.
        
        Args:
            user: Rejected user
            reason: Rejection reason
            
        Returns:
            True if notification sent successfully
        """
        if self.mock_mode:
            logger.info(
                f"[MOCK] Sending rejection notification to: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Cadastro Não Aprovado"
            )
            logger.info(
                f"[MOCK] Body: Olá {user.name},\n\n"
                f"Infelizmente seu cadastro não foi aprovado.\n"
                f"Motivo: {reason}\n\n"
                f"Se você acredita que isso foi um erro, entre em contato conosco."
            )
            return True
        
        # TODO: Implement actual email sending
        return False
    
    async def send_email_verification(
        self, user: UserEnhanced, verification_token: str
    ) -> bool:
        """
        Send email verification link to user.
        
        Args:
            user: User to verify
            verification_token: Token for verification
            
        Returns:
            True if email sent successfully
        """
        if self.mock_mode:
            verification_url = (
                f"{self.settings.frontend_url}/verify-email?token={verification_token}"
            )
            logger.info(
                f"[MOCK] Sending email verification to: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Verifique seu Email"
            )
            logger.info(
                f"[MOCK] Body: Olá {user.name},\n\n"
                f"Por favor, verifique seu email clicando no link abaixo:\n"
                f"{verification_url}\n\n"
                f"Este link expira em 24 horas."
            )
            logger.info(f"[MOCK] Verification URL: {verification_url}")
            return True
        
        # TODO: Implement actual email sending
        return False
    
    async def send_password_reset(
        self, user: UserEnhanced, reset_token: str
    ) -> bool:
        """
        Send password reset link to user.
        
        Args:
            user: User requesting reset
            reset_token: Token for password reset
            
        Returns:
            True if email sent successfully
        """
        if self.mock_mode:
            reset_url = (
                f"{self.settings.frontend_url}/reset-password?token={reset_token}"
            )
            logger.info(
                f"[MOCK] Sending password reset to: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Redefinir Senha"
            )
            logger.info(
                f"[MOCK] Body: Olá {user.name},\n\n"
                f"Você solicitou a redefinição de senha.\n"
                f"Clique no link abaixo para criar uma nova senha:\n"
                f"{reset_url}\n\n"
                f"Este link expira em 1 hora.\n"
                f"Se você não solicitou isso, ignore este email."
            )
            return True
        
        # TODO: Implement actual email sending
        return False
    
    async def send_account_locked_notification(
        self, user: UserEnhanced, attempts: int
    ) -> bool:
        """
        Send notification about account being locked due to failed attempts.
        
        Args:
            user: User whose account was locked
            attempts: Number of failed attempts
            
        Returns:
            True if notification sent successfully
        """
        if self.mock_mode:
            logger.info(
                f"[MOCK] Sending account locked notification to: {user.email}"
            )
            logger.info(
                f"[MOCK] Subject: Conta Bloqueada Temporariamente"
            )
            logger.info(
                f"[MOCK] Body: Olá {user.name},\n\n"
                f"Sua conta foi bloqueada temporariamente após {attempts} tentativas "
                f"de login falhadas.\n\n"
                f"A conta será desbloqueada automaticamente em 30 minutos.\n"
                f"Se você não fez essas tentativas, entre em contato imediatamente."
            )
            return True
        
        # TODO: Implement actual email sending
        return False
    
    def get_admin_emails(self) -> List[str]:
        """
        Get list of admin emails from settings.
        
        Returns:
            List of admin email addresses
        """
        # Get from environment variable (comma-separated)
        admin_emails_str = getattr(
            self.settings, 
            'admin_notification_emails', 
            'admin@sistema.com'
        )
        
        if isinstance(admin_emails_str, str):
            return [email.strip() for email in admin_emails_str.split(',')]
        
        return ['admin@sistema.com']  # Default fallback