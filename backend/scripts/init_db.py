#!/usr/bin/env python3
"""
Initialize database: run migrations and seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import engine, Base
from alembic.config import Config
from alembic import command
from scripts.seed import seed

def init_db():
    """Initialize database with migrations and seed data"""
    print("Running migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    print("Seeding database...")
    seed()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
