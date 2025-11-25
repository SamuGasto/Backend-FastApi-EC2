from sqlalchemy import Column, Integer, String, Float
from app.database import Base
from pydantic import BaseModel, Field
from typing import Optional


# Modelo SQLAlchemy (tabla en PostgreSQL)
class ProductDB(Base):
    """Modelo de base de datos para productos"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)


# Modelo Pydantic (validación y API)
class Product(BaseModel):
    """
    Modelo de Producto para la API.
    
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
    
    class Config:
        from_attributes = True
