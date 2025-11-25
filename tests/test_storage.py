"""
Unit tests para el sistema de almacenamiento en memoria.
Tests de inicialización y operaciones básicas.
"""
import pytest
from app.storage.memory import ProductStorage
from app.models.product import Product
from hypothesis import given, strategies as st


class TestProductStorage:
    """Tests para ProductStorage"""
    
    def test_storage_initializes_empty(self):
        """
        Test de estado inicial del almacenamiento.
        Verifica que el almacenamiento inicia vacío.
        Requirements: 6.4
        """
        storage = ProductStorage()
        
        # Verificar que el almacenamiento está vacío
        assert len(storage.get_all()) == 0
        assert storage.products == {}
        
        # Verificar que el contador de IDs inicia en 1
        assert storage.next_id == 1


class TestProductStorageProperties:
    """Property-based tests para ProductStorage"""
    
    @given(
        num_products=st.integers(min_value=1, max_value=100)
    )
    def test_product_id_uniqueness(self, num_products):
        """
        **Feature: fastapi-gunicorn-ec2, Property 5: Unicidad de identificadores**
        **Validates: Requirements 6.2, 6.5**
        
        Para cualquier conjunto de productos creados, todos los IDs asignados 
        deben ser únicos y no debe haber conflictos.
        """
        storage = ProductStorage()
        created_products = []
        
        # Crear múltiples productos aleatorios
        for i in range(num_products):
            product = Product(
                nombre=f"Producto {i}",
                precio=10.0 + i
            )
            created_product = storage.add(product)
            created_products.append(created_product)
        
        # Extraer todos los IDs
        product_ids = [p.id for p in created_products]
        
        # Verificar que todos los IDs son únicos
        assert len(product_ids) == len(set(product_ids)), \
            f"IDs duplicados encontrados: {product_ids}"
        
        # Verificar que ningún ID es None
        assert all(id is not None for id in product_ids), \
            "Algunos productos no tienen ID asignado"
        
        # Verificar que todos los IDs son positivos
        assert all(id > 0 for id in product_ids), \
            "Algunos IDs no son positivos"
