"""
Configuración de base de datos PostgreSQL con SQLAlchemy.

Este archivo maneja la conexión a PostgreSQL y proporciona
la sesión de base de datos para las rutas.

Para usar PostgreSQL:
1. Instala: pip install psycopg2-binary sqlalchemy
2. Configura DATABASE_URL en .env
3. Descomenta el código en main.py para crear tablas
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Cargar variables de entorno desde .env
from dotenv import load_dotenv

# Buscar .env en el directorio raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Leer URL de la base de datos desde variables de entorno
# Formato: postgresql://usuario:password@host:puerto/nombre_db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@localhost:5432/dbname"
)

# Debug: Mostrar si se cargó correctamente (solo para desarrollo)
if DATABASE_URL == "postgresql://user:pass@localhost:5432/dbname":
    import logging
    logging.warning("⚠️  DATABASE_URL no configurado! Usando default (localhost)")

# Crear engine de SQLAlchemy
# echo=True muestra las queries SQL en consola (útil para debug)
engine = create_engine(DATABASE_URL, echo=False)

# Crear clase de sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos de SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Dependencia para obtener sesión de base de datos.
    
    Uso en rutas:
        @router.get("/")
        def mi_ruta(db: Session = Depends(get_db)):
            # usar db aquí
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
