from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    """
    Modelo de Producto para la tienda.
    
    Attributes:
        id: Identificador único del producto (auto-generado)
        nombre: Nombre del producto (obligatorio, mínimo 1 carácter)
        precio: Precio del producto (obligatorio, debe ser mayor que 0)
        descripcion: Descripción opcional del producto
    """
    id: Optional[int] = None
    nombre: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    descripcion: Optional[str] = None
