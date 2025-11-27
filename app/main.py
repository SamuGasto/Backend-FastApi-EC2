import logging
import os
from fastapi import FastAPI
from app.routes import products

# Solo crear tablas si no estamos en modo test
if os.getenv("TESTING") != "1":
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="API de Productos",
    description="API REST para gestión de productos con PostgreSQL",
    version="1.0.0"
)

# Include product routes
app.include_router(products.router)

logger.info("FastAPI application initialized with PostgreSQL")


@app.get("/")
async def root():
    """Endpoint raíz que retorna un mensaje de bienvenida"""
    return {"message": "Bienvenido a la API de Productos"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint para ALB y Auto Scaling Group.
    Verifica que la app esté corriendo y pueda conectarse a la DB.
    """
    try:
        # Verificar conexión a base de datos
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "productos-api",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "productos-api",
            "database": "disconnected",
            "error": str(e)
        }
