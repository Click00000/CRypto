#!/usr/bin/env python3
"""
Seed script for initial data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import Base, User, Exchange, UserRole
from app.core.config import settings
import secrets

def seed():
    db = SessionLocal()
    try:
        # Create tables if not exist
        Base.metadata.create_all(bind=engine)
        
        # Create admin user
        admin_email = settings.ADMIN_EMAIL.lower().strip()
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                role=UserRole.ADMIN,
                email_verified_at=None  # Will be verified on first login
            )
            db.add(admin_user)
            print(f"Created admin user: {admin_email}")
        else:
            # Ensure admin role
            admin_user.role = UserRole.ADMIN
            print(f"Admin user already exists: {admin_email}")
        
        # Create sample exchanges
        sample_exchanges = [
            {"name": "Binance", "slug": "binance"},
            {"name": "Coinbase", "slug": "coinbase"},
            {"name": "OKX", "slug": "okx"},
            {"name": "Bybit", "slug": "bybit"},
            {"name": "Kraken", "slug": "kraken"},
        ]
        
        for ex_data in sample_exchanges:
            existing = db.query(Exchange).filter(Exchange.slug == ex_data["slug"]).first()
            if not existing:
                exchange = Exchange(**ex_data)
                db.add(exchange)
                print(f"Created exchange: {ex_data['name']}")
            else:
                print(f"Exchange already exists: {ex_data['name']}")
        
        db.commit()
        print("Seed completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
