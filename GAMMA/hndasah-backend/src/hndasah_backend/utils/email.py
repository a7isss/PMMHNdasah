"""
Email utilities for WhatsApp PM System v3.0 (Gamma)
SMTP email sending with templates and async support
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import structlog
from jinja2 import Template
from ..config import settings

logger = structlog.get_logger(__name__)


class EmailService:
    """Email service for sending notifications and password resets."""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

        # Check if email is configured
        self.enabled = bool(
            self.smtp_server and
            self.smtp_username and
            self.smtp_password
        )

        if not self.enabled:
            logger.warning("Email service not configured - emails will not be sent")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email with HTML and optional text content."""
        if not self.enabled:
            logger.info("Email service disabled, skipping email send", to=to_email, subject=subject)
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            logger.info("Email sent successfully", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error(
                "Failed to send email",
                to=to_email,
                subject=subject,
                error=str(e)
            )
            return False

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        subject = "Password Reset - WhatsApp PM"
        html_content = self._get_password_reset_template(reset_url)
        text_content = f"""
        Password Reset Request

        You requested a password reset for your WhatsApp PM account.

        Click the link below to reset your password:
        {reset_url}

        This link will expire in 24 hours.

        If you didn't request this reset, please ignore this email.

        Best regards,
        WhatsApp PM Team
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_welcome_email(self, to_email: str, user_name: str, tenant_name: str) -> bool:
        """Send welcome email to new users."""
        subject = f"Welcome to WhatsApp PM - {tenant_name}"
        html_content = self._get_welcome_template(user_name, tenant_name)
        text_content = f"""
        Welcome to WhatsApp PM!

        Hi {user_name},

        Welcome to WhatsApp PM! You've been added to the {tenant_name} organization.

        You can now log in to your account and start managing construction projects with AI-powered insights.

        Best regards,
        WhatsApp PM Team
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        project_name: Optional[str] = None
    ) -> bool:
        """Send notification email."""
        html_content = self._get_notification_template(subject, message, project_name)
        return await self.send_email(to_email, subject, html_content, message)

    def _get_password_reset_template(self, reset_url: str) -> str:
        """Get HTML template for password reset email."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }
                .header { text-align: center; margin-bottom: 30px; }
                .button { display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                    <p>You requested a password reset for your WhatsApp PM account.</p>
                </div>

                <p>Click the button below to reset your password:</p>

                <a href="{{ reset_url }}" class="button">Reset Password</a>

                <p><small>This link will expire in 24 hours.</small></p>

                <p>If the button doesn't work, copy and paste this URL into your browser:</p>
                <p><small>{{ reset_url }}</small></p>

                <p>If you didn't request this reset, please ignore this email.</p>

                <div class="footer">
                    <p>Best regards,<br>WhatsApp PM Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        return Template(template).render(reset_url=reset_url)

    def _get_welcome_template(self, user_name: str, tenant_name: str) -> str:
        """Get HTML template for welcome email."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to WhatsApp PM</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }
                .header { text-align: center; margin-bottom: 30px; }
                .features { margin: 20px 0; }
                .feature { margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to WhatsApp PM!</h1>
                    <p>Hi {{ user_name }}, welcome to the {{ tenant_name }} organization.</p>
                </div>

                <p>You can now log in to your account and start managing construction projects with AI-powered insights.</p>

                <div class="features">
                    <h3>What you can do:</h3>
                    <div class="feature">📱 Manage projects with WhatsApp integration</div>
                    <div class="feature">🤖 Get AI-powered insights and recommendations</div>
                    <div class="feature">📊 Track costs and schedules in real-time</div>
                    <div class="feature">👥 Collaborate with your team seamlessly</div>
                </div>

                <div class="footer">
                    <p>Best regards,<br>WhatsApp PM Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        return Template(template).render(user_name=user_name, tenant_name=tenant_name)

    def _get_notification_template(self, subject: str, message: str, project_name: Optional[str] = None) -> str:
        """Get HTML template for notification emails."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }
                .header { margin-bottom: 20px; }
                .message { margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{{ subject }}</h2>
                    {% if project_name %}
                    <p><strong>Project:</strong> {{ project_name }}</p>
                    {% endif %}
                </div>

                <div class="message">
                    {{ message|replace('\n', '<br>') }}
                </div>

                <div class="footer">
                    <p>This is an automated notification from WhatsApp PM.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return Template(template).render(
            subject=subject,
            message=message,
            project_name=project_name
        )


# Global email service instance
email_service = EmailService()


async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send password reset email (convenience function)."""
    return await email_service.send_password_reset_email(to_email, reset_token)

