from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User, MagicLinkToken, UserRole
from app.core.security import generate_magic_link_token, hash_token, verify_token_hash
from app.services.email import get_email_service
import logging
import secrets

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = get_email_service()
    
    def request_magic_link(self, email: str, marketing_opt_in: bool = False) -> dict:
        """Request magic link - create or get user, create token, send email"""
        # Normalize email
        email = email.lower().strip()
        
        # Get or create user
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Determine role (first user or admin email gets admin)
            role = UserRole.ADMIN if self._is_admin_email(email) else UserRole.USER
            
            user = User(
                email=email,
                role=role,
                marketing_opt_in=marketing_opt_in,
                marketing_opt_in_at=datetime.utcnow() if marketing_opt_in else None,
                unsubscribe_token=secrets.token_urlsafe(32) if marketing_opt_in else None
            )
            self.db.add(user)
            self.db.flush()
            logger.info(f"Created new user: {email} with role: {role}")
        else:
            # Update marketing opt-in if provided
            if marketing_opt_in and not user.marketing_opt_in:
                user.marketing_opt_in = True
                user.marketing_opt_in_at = datetime.utcnow()
                if not user.unsubscribe_token:
                    user.unsubscribe_token = secrets.token_urlsafe(32)
        
        # Create magic link token
        token = generate_magic_link_token()
        token_hash = hash_token(token)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        magic_token = MagicLinkToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.db.add(magic_token)
        self.db.commit()
        
        # Send email
        self.email_service.send_magic_link(email, token, marketing_opt_in)
        
        return {"message": "Magic link sent to your email"}
    
    def consume_magic_link(self, token: str) -> Optional[User]:
        """Validate and consume magic link token, return user"""
        # Find unused, non-expired token
        now = datetime.utcnow()
        magic_tokens = self.db.query(MagicLinkToken).filter(
            MagicLinkToken.used_at.is_(None),
            MagicLinkToken.expires_at > now
        ).all()
        
        for mt in magic_tokens:
            if verify_token_hash(token, mt.token_hash):
                # Mark as used
                mt.used_at = datetime.utcnow()
                
                # Verify user email if not already verified
                user = mt.user
                if not user.email_verified_at:
                    user.email_verified_at = datetime.utcnow()
                
                self.db.commit()
                return user
        
        return None
    
    def _is_admin_email(self, email: str) -> bool:
        """Check if email matches admin email from config"""
        from app.core.config import settings
        return email.lower() == settings.ADMIN_EMAIL.lower()
    
    def unsubscribe(self, unsubscribe_token: str) -> bool:
        """Unsubscribe user from marketing emails"""
        user = self.db.query(User).filter(
            User.unsubscribe_token == unsubscribe_token
        ).first()
        
        if not user:
            return False
        
        user.unsubscribed_at = datetime.utcnow()
        user.marketing_opt_in = False
        self.db.commit()
        
        self.email_service.send_unsubscribe_confirmation(user.email)
        return True
