"""
Asynchronous notification service using FastAPI BackgroundTasks (AE-048).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from fastapi import BackgroundTasks
from jinja2 import Template, Environment, FileSystemLoader
import os

from src.domain.entities.user_enhanced import UserEnhanced
from src.infrastructure.config import Settings
from src.infrastructure.services.email_service import EmailService

logger = logging.getLogger(__name__)


class AsyncNotificationService:
    """
    Asynchronous notification service for sending emails in background.
    
    Uses FastAPI BackgroundTasks for queue management.
    """
    
    def __init__(self, settings: Settings, email_service: Optional[EmailService] = None):
        """
        Initialize async notification service.
        
        Args:
            settings: Application settings
            email_service: Email service instance
        """
        self.settings = settings
        self.email_service = email_service or EmailService(settings)
        
        # Setup Jinja2 for template rendering
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "templates"
        )
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render email template with context.
        
        Args:
            template_name: Template file name
            context: Template context variables
            
        Returns:
            Rendered HTML content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            # Add common context
            context['current_year'] = datetime.now().year
            context['app_name'] = self.settings.app_name
            context['frontend_url'] = self.settings.frontend_url
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return ""
    
    async def _send_email_task(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ):
        """
        Background task to send email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            template_name: Template file name
            context: Template context
        """
        try:
            # Render template
            html_content = self._render_template(template_name, context)
            
            if html_content:
                # Send email
                await self.email_service.send_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content
                )
                logger.info(f"Email sent successfully to {to_email}")
            else:
                logger.error(f"Failed to render template for {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
    
    def send_verification_email(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        verification_link: str
    ):
        """
        Queue verification email to be sent in background.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: User to verify
            verification_link: Verification URL
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'user_role': user.role.value if user.role else 'COLABORADOR',
            'verification_link': verification_link,
            'expire_hours': self.settings.email_verification_expire_hours
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Verifique seu e-mail - Sistema de Coleta",
            template_name="verification_email.html",
            context=context
        )
        
        logger.info(f"Verification email queued for {user.email}")
    
    def send_welcome_email(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        approved_by: str
    ):
        """
        Queue welcome email after approval.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: Approved user
            approved_by: Admin who approved
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'user_role': user.role.value if user.role else 'COLABORADOR',
            'approved_by': approved_by,
            'approved_at': user.approved_at.strftime('%d/%m/%Y %H:%M') if user.approved_at else '',
            'login_url': f"{self.settings.frontend_url}/login"
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Conta Aprovada! Bem-vindo ao Sistema de Coleta",
            template_name="welcome_email.html",
            context=context
        )
        
        logger.info(f"Welcome email queued for {user.email}")
    
    def send_rejection_email(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        rejected_by: str,
        reason: Optional[str] = None
    ):
        """
        Queue rejection email.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: Rejected user
            rejected_by: Admin who rejected
            reason: Rejection reason
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'user_role': user.role.value if user.role else 'COLABORADOR',
            'rejected_by': rejected_by,
            'rejected_at': user.rejected_at.strftime('%d/%m/%Y %H:%M') if user.rejected_at else '',
            'rejection_reason': reason,
            'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else ''
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Atualização sobre seu cadastro - Sistema de Coleta",
            template_name="rejection_email.html",
            context=context
        )
        
        logger.info(f"Rejection email queued for {user.email}")
    
    def send_admin_notification(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        admin_emails: List[str]
    ):
        """
        Queue admin notification for new user registration.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: New user pending approval
            admin_emails: List of admin emails
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'user_role': user.role.value if user.role else 'COLABORADOR',
            'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
            'email_verified': user.email_verified,
            'request_id': user.id,
            'admin_dashboard_url': f"{self.settings.frontend_url}/admin/users/pending",
            'pending_count': 0  # Will be updated by service
        }
        
        for admin_email in admin_emails:
            background_tasks.add_task(
                self._send_email_task,
                to_email=admin_email,
                subject=f"Nova Solicitação de Cadastro - {user.name}",
                template_name="admin_notification.html",
                context=context
            )
        
        logger.info(f"Admin notifications queued for new user {user.email}")
    
    def send_account_blocked_email(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        failed_attempts: int,
        unlock_time: datetime
    ):
        """
        Queue account blocked notification.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: Blocked user
            failed_attempts: Number of failed attempts
            unlock_time: When account will be unlocked
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'failed_attempts': failed_attempts,
            'max_attempts': self.settings.max_login_attempts,
            'blocked_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'unlock_at': unlock_time.strftime('%d/%m/%Y %H:%M'),
            'block_duration': self.settings.account_lock_minutes
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Conta Bloqueada - Sistema de Coleta",
            template_name="account_blocked.html",
            context=context
        )
        
        logger.info(f"Account blocked email queued for {user.email}")
    
    def send_password_reset_email(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced,
        reset_link: str
    ):
        """
        Queue password reset email.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: User requesting reset
            reset_link: Password reset URL
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'reset_link': reset_link,
            'expire_hours': 2,  # Password reset expires in 2 hours
            'requested_at': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Redefinição de Senha - Sistema de Coleta",
            template_name="password_reset.html",
            context=context
        )
        
        logger.info(f"Password reset email queued for {user.email}")
    
    def send_approval_confirmation(
        self,
        background_tasks: BackgroundTasks,
        user: UserEnhanced
    ):
        """
        Queue confirmation email when user submits registration.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
            user: User who registered
        """
        context = {
            'user_name': user.name,
            'user_email': user.email,
            'user_role': user.role.value if user.role else 'COLABORADOR',
            'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
            'email_verified': user.email_verified,
            'request_id': user.id
        }
        
        background_tasks.add_task(
            self._send_email_task,
            to_email=user.email,
            subject="Solicitação Recebida - Sistema de Coleta",
            template_name="approval_request.html",
            context=context
        )
        
        logger.info(f"Approval confirmation email queued for {user.email}")