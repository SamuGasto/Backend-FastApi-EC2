import logging
from fastapi import FastAPI
from app.routes import products

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="API de Productos",
    description="API básica para gestión de productos de tienda",
    version="1.0.0"
)

# Include product routes
app.include_router(products.router)

logger.info("FastAPI application initialized")


@app.get("/")
async def root():
    """Endpoint raíz que retorna un mensaje de bienvenida"""
    return {"message": "Bienvenido a la API de Productos"}
