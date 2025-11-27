"""
Configuración de base de datos PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# Crear engine con configuración de pool y timeouts
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10,  # Conexiones adicionales permitidas
    pool_recycle=3600,  # Reciclar conexiones cada hora
    connect_args={
        "connect_timeout": 10,  # Timeout de conexión en segundos
        "options": "-c statement_timeout=30000"  # Timeout de queries en ms
    }
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
