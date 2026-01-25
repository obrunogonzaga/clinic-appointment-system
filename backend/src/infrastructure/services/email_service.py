"""
Email service for sending notifications with real SMTP support.
"""

import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, Template

from src.domain.entities.user_enhanced import UserEnhanced
from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails with SMTP support and HTML templates.

    Supports multiple email providers (SMTP, SendGrid, AWS SES).
    Currently implements SMTP with async support.
    """

    def __init__(self, settings: Settings):
        """
        Initialize email service.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Email configuration
        self.smtp_host = getattr(settings, "smtp_host", None)
        self.smtp_port = getattr(settings, "smtp_port", 587)
        self.smtp_username = getattr(settings, "smtp_username", None)
        self.smtp_password = getattr(settings, "smtp_password", None)
        self.smtp_from_email = getattr(
            settings, "smtp_from_email", "noreply@sistema.com"
        )
        self.smtp_from_name = getattr(
            settings, "smtp_from_name", "Sistema de Coleta"
        )

        # Check if email is configured
        self.is_configured = bool(
            self.smtp_host and self.smtp_username and self.smtp_password
        )

        # Frontend URL for links
        self.frontend_url = getattr(
            settings, "frontend_url", "http://localhost:3000"
        )

        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)), autoescape=True
        )

        # Create default templates if they don't exist
        self._create_default_templates(template_dir)

    def _create_default_templates(self, template_dir: Path):
        """Create default email templates if they don't exist."""

        # Base template
        base_template = template_dir / "base.html"
        if not base_template.exists():
            base_template.write_text(
                """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #4CAF50;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #4CAF50;
            margin: 0;
        }
        .content {
            margin: 20px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }
        .alert {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #28a745;
        }
        .danger {
            background-color: #f8d7da;
            border: 1px solid #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
        <div class="footer">
            <p>© 2025 Sistema de Coleta. Todos os direitos reservados.</p>
            <p>Este é um email automático, por favor não responda.</p>
        </div>
    </div>
</body>
</html>"""
            )

        # Email verification template
        verification_template = template_dir / "verification.html"
        if not verification_template.exists():
            verification_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>Olá {{ user_name }}!</h2>
    <p>Obrigado por se cadastrar em nosso sistema.</p>
    <p>Para completar seu cadastro e verificar seu email, clique no botão abaixo:</p>
    
    <div style="text-align: center;">
        <a href="{{ verification_url }}" class="button">Verificar Email</a>
    </div>
    
    <p style="font-size: 14px; color: #666;">
        Ou copie e cole este link em seu navegador:<br>
        <code>{{ verification_url }}</code>
    </p>
    
    <div class="alert">
        <strong>⚠️ Importante:</strong> Este link expira em 24 horas.
    </div>
    
    <p>Se você não criou uma conta em nosso sistema, ignore este email.</p>
{% endblock %}"""
            )

        # Welcome (approval) template
        welcome_template = template_dir / "welcome.html"
        if not welcome_template.exists():
            welcome_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>Bem-vindo(a), {{ user_name }}!</h2>
    
    <div class="success">
        <strong>✅ Seu cadastro foi aprovado!</strong>
    </div>
    
    <p>Temos o prazer de informar que sua solicitação de cadastro foi aprovada pela administração.</p>
    
    <h3>Seus dados de acesso:</h3>
    <ul>
        <li><strong>Email:</strong> {{ user_email }}</li>
        <li><strong>Perfil:</strong> {{ user_role }}</li>
        <li><strong>Status:</strong> Ativo</li>
    </ul>
    
    <p>Agora você pode acessar o sistema com suas credenciais:</p>
    
    <div style="text-align: center;">
        <a href="{{ login_url }}" class="button">Acessar Sistema</a>
    </div>
    
    <p>Se tiver alguma dúvida, entre em contato com o suporte.</p>
{% endblock %}"""
            )

        # Rejection template
        rejection_template = template_dir / "rejection.html"
        if not rejection_template.exists():
            rejection_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>Olá {{ user_name }}</h2>
    
    <div class="danger">
        <strong>Cadastro não aprovado</strong>
    </div>
    
    <p>Infelizmente, sua solicitação de cadastro não foi aprovada pela administração.</p>
    
    <h3>Motivo:</h3>
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <em>{{ rejection_reason }}</em>
    </div>
    
    <p>Se você acredita que houve um engano ou gostaria de mais informações, entre em contato com nosso suporte.</p>
    
    <p><strong>Email de suporte:</strong> suporte@sistema.com</p>
{% endblock %}"""
            )

        # Password reset template
        password_reset_template = template_dir / "password_reset.html"
        if not password_reset_template.exists():
            password_reset_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>Redefinição de Senha</h2>
    
    <p>Olá {{ user_name }},</p>
    
    <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
    
    <div style="text-align: center;">
        <a href="{{ reset_url }}" class="button">Redefinir Senha</a>
    </div>
    
    <p style="font-size: 14px; color: #666;">
        Ou copie e cole este link em seu navegador:<br>
        <code>{{ reset_url }}</code>
    </p>
    
    <div class="alert">
        <strong>⚠️ Importante:</strong> Este link expira em 1 hora.
    </div>
    
    <p>Se você não solicitou a redefinição de senha, ignore este email. Sua senha permanecerá inalterada.</p>
    
    <p style="color: #dc3545;"><strong>Segurança:</strong> Por motivos de segurança, nunca compartilhe este link com outras pessoas.</p>
{% endblock %}"""
            )

        # Account locked template
        account_locked_template = template_dir / "account_locked.html"
        if not account_locked_template.exists():
            account_locked_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>⚠️ Conta Bloqueada Temporariamente</h2>
    
    <p>Olá {{ user_name }},</p>
    
    <div class="danger">
        <strong>Sua conta foi bloqueada temporariamente devido a múltiplas tentativas de login falhadas.</strong>
    </div>
    
    <h3>Detalhes:</h3>
    <ul>
        <li><strong>Número de tentativas:</strong> {{ attempts }}</li>
        <li><strong>Horário do bloqueio:</strong> {{ locked_at }}</li>
        <li><strong>Desbloqueio automático em:</strong> 30 minutos</li>
    </ul>
    
    <p><strong>O que fazer agora?</strong></p>
    <ul>
        <li>Aguarde 30 minutos para tentar novamente</li>
        <li>Certifique-se de usar a senha correta</li>
        <li>Se esqueceu sua senha, solicite uma redefinição</li>
    </ul>
    
    <div class="alert">
        <strong>🔒 Importante:</strong> Se você não fez essas tentativas de login, 
        sua conta pode estar comprometida. Entre em contato com o suporte imediatamente.
    </div>
    
    <p><strong>Email de suporte:</strong> suporte@sistema.com</p>
{% endblock %}"""
            )

        # New user notification for admins
        admin_notification_template = template_dir / "admin_new_user.html"
        if not admin_notification_template.exists():
            admin_notification_template.write_text(
                """{% extends "base.html" %}
{% block content %}
    <h2>📋 Novo Cadastro Pendente de Aprovação</h2>
    
    <p>Um novo usuário se cadastrou no sistema e aguarda sua aprovação.</p>
    
    <h3>Dados do Usuário:</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Nome:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{{ user_name }}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Email:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{{ user_email }}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Perfil Solicitado:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{{ user_role }}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Data do Cadastro:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{{ registration_date }}</td>
        </tr>
        {% if user_department %}
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Departamento:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{{ user_department }}</td>
        </tr>
        {% endif %}
    </table>
    
    <div style="text-align: center; margin-top: 30px;">
        <a href="{{ admin_url }}" class="button">Revisar Cadastro</a>
    </div>
    
    <p style="font-size: 14px; color: #666;">
        Acesse o painel administrativo para aprovar ou rejeitar este cadastro.
    </p>
{% endblock %}"""
            )

    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send email asynchronously.

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            html_content: HTML email content
            text_content: Optional plain text content

        Returns:
            True if email sent successfully
        """
        if not self.is_configured:
            logger.warning("Email service not configured, skipping email send")
            logger.info(f"[MOCK EMAIL] To: {to_emails}, Subject: {subject}")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            message["To"] = ", ".join(to_emails)

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # Send email asynchronously
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True,
            )

            logger.info(f"Email sent successfully to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def render_template(self, template_name: str, **context) -> str:
        """
        Render email template with context.

        Args:
            template_name: Template file name
            **context: Template variables

        Returns:
            Rendered HTML content
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            # Return simple fallback
            return f"<html><body><p>{context.get('message', 'Email content')}</p></body></html>"

    def _serialize_role(self, role: Any) -> str:
        """Normalize role enumeration/string for template context."""
        if hasattr(role, "value"):
            return str(role.value)
        if isinstance(role, str) and role:
            return role
        return "colaborador"

    async def send_verification_email(
        self, user: UserEnhanced, verification_token: str
    ) -> bool:
        """
        Send email verification to user.

        Args:
            user: User to verify
            verification_token: Verification token

        Returns:
            True if sent successfully
        """
        verification_url = (
            f"{self.frontend_url}/verify-email/{verification_token}"
        )

        html_content = self.render_template(
            "verification.html",
            title="Verificação de Email",
            user_name=user.name,
            verification_url=verification_url,
        )

        return await self.send_email(
            [user.email],
            "Verifique seu Email - Sistema de Coleta",
            html_content,
        )

    async def send_welcome_email(self, user: UserEnhanced) -> bool:
        """
        Send welcome email after approval.

        Args:
            user: Approved user

        Returns:
            True if sent successfully
        """
        html_content = self.render_template(
            "welcome.html",
            title="Bem-vindo ao Sistema!",
            user_name=user.name,
            user_email=user.email,
            user_role=self._serialize_role(user.role),
            login_url=f"{self.frontend_url}/login",
        )

        return await self.send_email(
            [user.email], "Cadastro Aprovado - Bem-vindo!", html_content
        )

    async def send_rejection_email(
        self, user: UserEnhanced, reason: str
    ) -> bool:
        """
        Send rejection notification.

        Args:
            user: Rejected user
            reason: Rejection reason

        Returns:
            True if sent successfully
        """
        html_content = self.render_template(
            "rejection.html",
            title="Cadastro Não Aprovado",
            user_name=user.name,
            rejection_reason=reason,
        )

        return await self.send_email(
            [user.email], "Cadastro Não Aprovado", html_content
        )

    async def send_password_reset_email(
        self, user: UserEnhanced, reset_token: str
    ) -> bool:
        """
        Send password reset email.

        Args:
            user: User requesting reset
            reset_token: Reset token

        Returns:
            True if sent successfully
        """
        reset_url = f"{self.frontend_url}/reset-password/{reset_token}"

        html_content = self.render_template(
            "password_reset.html",
            title="Redefinir Senha",
            user_name=user.name,
            reset_url=reset_url,
        )

        return await self.send_email(
            [user.email], "Redefinição de Senha", html_content
        )

    async def send_account_locked_email(
        self, user: UserEnhanced, attempts: int
    ) -> bool:
        """
        Send account locked notification.

        Args:
            user: User whose account was locked
            attempts: Number of failed attempts

        Returns:
            True if sent successfully
        """
        html_content = self.render_template(
            "account_locked.html",
            title="Conta Bloqueada",
            user_name=user.name,
            attempts=attempts,
            locked_at=datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"),
        )

        return await self.send_email(
            [user.email], "⚠️ Conta Bloqueada Temporariamente", html_content
        )

    async def send_admin_notification(
        self, user: UserEnhanced, admin_emails: List[str]
    ) -> bool:
        """
        Notify admins about new user registration.

        Args:
            user: New user
            admin_emails: List of admin emails

        Returns:
            True if sent successfully
        """
        role_value = self._serialize_role(user.role)

        html_content = self.render_template(
            "admin_new_user.html",
            title="Novo Cadastro Pendente",
            user_name=user.name,
            user_email=user.email,
            user_role=role_value,
            user_department=user.metadata.department,
            registration_date=user.created_at.strftime("%d/%m/%Y %H:%M"),
            admin_url=f"{self.frontend_url}/admin/users/pending",
        )

        return await self.send_email(
            admin_emails,
            f"📋 Novo Cadastro Pendente - {user.name}",
            html_content,
        )
