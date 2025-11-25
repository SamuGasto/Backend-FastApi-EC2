from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.product import Product, ProductDB
from app.database import get_db

# Create router for product endpoints
router = APIRouter(prefix="/productos", tags=["productos"])


@router.post("/", response_model=Product, status_code=201)
async def create_product(product: Product, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto en PostgreSQL.
    
    Args:
        product: Datos del producto a crear (nombre, precio, descripcion)
        db: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        Product: El producto creado con su ID asignado
    """
    db_product = ProductDB(
        nombre=product.nombre,
        precio=product.precio,
        descripcion=product.descripcion
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[Product])
async def list_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos desde PostgreSQL.
    
    Args:
        db: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        List[Product]: Lista de todos los productos
    """
    products = db.query(ProductDB).all()
    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto específico por ID.
    
    Args:
        product_id: ID del producto a buscar
        db: Sesión de base de datos
    
    Returns:
        Product: El producto encontrado
    
    Raises:
        HTTPException: 404 si el producto no existe
    """
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product: Product, db: Session = Depends(get_db)):
    """
    Actualiza un producto existente.
    
    Args:
        product_id: ID del producto a actualizar
        product: Nuevos datos del producto
        db: Sesión de base de datos
    
    Returns:
        Product: El producto actualizado
    
    Raises:
        HTTPException: 404 si el producto no existe
    """
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db_product.nombre = product.nombre
    db_product.precio = product.precio
    db_product.descripcion = product.descripcion
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto.
    
    Args:
        product_id: ID del producto a eliminar
        db: Sesión de base de datos
    
    Raises:
        HTTPException: 404 si el producto no existe
    """
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_product)
    db.commit()
    return None
