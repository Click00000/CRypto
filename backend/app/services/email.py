from typing import Optional
from app.core.config import settings
import resend
import logging

logger = logging.getLogger(__name__)

# Initialize Resend client
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Email service with abstraction for swapping providers"""
    
    @staticmethod
    def send_magic_link(email: str, token: str, marketing_opt_in: bool = False) -> bool:
        """Send magic link email"""
        try:
            login_url = f"{settings.APP_BASE_URL}/auth/callback?token={token}"
            
            subject = "Your Exchange Flow Intelligence Login Link"
            html_content = f"""
            <html>
            <body>
                <h2>Login to Exchange Flow Intelligence</h2>
                <p>Click the link below to log in:</p>
                <p><a href="{login_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login</a></p>
                <p>Or copy this URL: {login_url}</p>
                <p>This link expires in 1 hour.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">If you didn't request this, please ignore this email.</p>
            </body>
            </html>
            """
            
            params = {
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": subject,
                "html": html_content,
            }
            
            email_response = resend.Emails.send(params)
            logger.info(f"Magic link email sent to {email}: {email_response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send magic link email: {e}")
            return False
    
    @staticmethod
    def send_unsubscribe_confirmation(email: str) -> bool:
        """Send unsubscribe confirmation email"""
        try:
            subject = "You've been unsubscribed"
            html_content = """
            <html>
            <body>
                <h2>Unsubscribed Successfully</h2>
                <p>You have been unsubscribed from marketing emails.</p>
                <p>You will continue to receive important account notifications.</p>
            </body>
            </html>
            """
            
            params = {
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": subject,
                "html": html_content,
            }
            
            resend.Emails.send(params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send unsubscribe confirmation: {e}")
            return False


# Factory function for future provider swapping
def get_email_service() -> EmailService:
    """Get email service instance (can be swapped for SendGrid/SES)"""
    return EmailService()
