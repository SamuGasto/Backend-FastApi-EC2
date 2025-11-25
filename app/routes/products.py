from fastapi import APIRouter, HTTPException
from typing import List
from app.models.product import Product
from app.storage.memory import ProductStorage

# Create router for product endpoints
router = APIRouter(prefix="/productos", tags=["productos"])

# Initialize product storage (singleton instance)
storage = ProductStorage()


@router.post("/", response_model=Product, status_code=201)
async def create_product(product: Product):
    """
    Crea un nuevo producto en el almacenamiento.
    
    Args:
        product: Datos del producto a crear (nombre, precio, descripcion)
    
    Returns:
        Product: El producto creado con su ID asignado
    
    Raises:
        HTTPException: 422 si los datos son inválidos (validado por Pydantic)
    """
    created_product = storage.add(product)
    return created_product


@router.get("/", response_model=List[Product])
async def list_products():
    """
    Lista todos los productos almacenados.
    
    Returns:
        List[Product]: Lista de todos los productos en el sistema
    """
    products = storage.get_all()
    return products
