"""
Tests básicos para verificar configuración.
"""

import pytest
from pathlib import Path


def test_env_example_exists():
    """Verifica que .env.example existe"""
    env_example = Path(__file__).parent.parent / '.env.example'
    assert env_example.exists()


def test_config_loads():
    """Verifica que la configuración se carga"""
    from app.config import DATABASE_URL, APP_PORT
    
    assert DATABASE_URL is not None
    assert APP_PORT is not None
    assert isinstance(APP_PORT, int)


def test_database_imports():
    """Verifica que database.py se puede importar"""
    from app.database import engine, Base, get_db
    
    assert engine is not None
    assert Base is not None
    assert get_db is not None
