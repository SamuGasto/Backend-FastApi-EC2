"""
Unit tests para el modelo Product.
Tests de validación de campos obligatorios y inicialización.
"""
import pytest
from pydantic import ValidationError
from app.models.product import Product


class TestProductModel:
    """Tests para el modelo Product"""
    
    def test_product_initialization_with_valid_data(self):
        """Test de inicialización con datos válidos"""
        product = Product(
            nombre="Laptop",
            precio=999.99,
            descripcion="Laptop de alta gama"
        )
        
        assert product.nombre == "Laptop"
        assert product.precio == 999.99
        assert product.descripcion == "Laptop de alta gama"
        assert product.id is None
    
    def test_product_initialization_minimal_fields(self):
        """Test de inicialización con campos mínimos obligatorios"""
        product = Product(nombre="Mouse", precio=25.50)
        
        assert product.nombre == "Mouse"
        assert product.precio == 25.50
        assert product.descripcion is None
        assert product.id is None
    
    def test_product_missing_nombre_raises_error(self):
        """Test que nombre es campo obligatorio"""
        with pytest.raises(ValidationError) as exc_info:
            Product(precio=100.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('nombre',) for error in errors)
    
    def test_product_missing_precio_raises_error(self):
        """Test que precio es campo obligatorio"""
        with pytest.raises(ValidationError) as exc_info:
            Product(nombre="Producto")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('precio',) for error in errors)
    
    def test_product_empty_nombre_raises_error(self):
        """Test que nombre no puede ser vacío (min_length=1)"""
        with pytest.raises(ValidationError) as exc_info:
            Product(nombre="", precio=50.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('nombre',) for error in errors)
    
    def test_product_precio_must_be_positive(self):
        """Test que precio debe ser mayor que 0"""
        with pytest.raises(ValidationError) as exc_info:
            Product(nombre="Producto", precio=0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('precio',) for error in errors)
    
    def test_product_precio_negative_raises_error(self):
        """Test que precio no puede ser negativo"""
        with pytest.raises(ValidationError) as exc_info:
            Product(nombre="Producto", precio=-10.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('precio',) for error in errors)


# Property-Based Tests
from hypothesis import given, strategies as st
import json


class TestProductProperties:
    """Property-based tests para el modelo Product"""
    
    @given(
        nombre=st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
        precio=st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        descripcion=st.one_of(st.none(), st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), max_size=500))
    )
    def test_product_serialization_round_trip(self, nombre, precio, descripcion):
        """
        **Feature: fastapi-gunicorn-ec2, Property 1: Serialización round trip de Producto**
        **Validates: Requirements 2.5**
        
        Para cualquier Producto válido, serializarlo a JSON y luego deserializarlo 
        debe producir un objeto equivalente.
        """
        # Crear producto original
        original = Product(nombre=nombre, precio=precio, descripcion=descripcion)
        
        # Serializar a JSON
        json_str = original.model_dump_json()
        
        # Deserializar desde JSON
        json_data = json.loads(json_str)
        reconstructed = Product(**json_data)
        
        # Verificar equivalencia
        assert reconstructed.nombre == original.nombre
        assert reconstructed.precio == original.precio
        assert reconstructed.descripcion == original.descripcion
        assert reconstructed.id == original.id
    
    @given(
        data=st.one_of(
            # Caso 1: nombre vacío (string vacío) - viola min_length=1
            st.fixed_dictionaries({
                'nombre': st.just(''),
                'precio': st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
            }),
            # Caso 2: precio cero - viola gt=0
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                'precio': st.just(0.0)
            }),
            # Caso 3: precio negativo - viola gt=0
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                'precio': st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False)
            }),
            # Caso 4: precio NaN - viola gt=0
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                'precio': st.just(float('nan'))
            }),
            # Caso 5: tipo incorrecto para nombre (número) - viola tipo str
            st.fixed_dictionaries({
                'nombre': st.integers(),
                'precio': st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
            }),
            # Caso 6: tipo incorrecto para precio (string no numérico) - viola tipo float
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                'precio': st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10)
            })
        )
    )
    def test_product_rejects_invalid_data(self, data):
        """
        **Feature: fastapi-gunicorn-ec2, Property 4: Rechazo de datos inválidos**
        **Validates: Requirements 2.2, 2.4, 3.4, 7.1**
        
        Para cualquier dato inválido (nombre vacío, precio negativo o cero, tipos incorrectos),
        el sistema debe rechazar la creación y retornar un error de validación.
        """
        # Intentar crear producto con datos inválidos
        with pytest.raises(ValidationError) as exc_info:
            Product(**data)
        
        # Verificar que se generó un error de validación
        errors = exc_info.value.errors()
        assert len(errors) > 0
        
        # Verificar que el error está relacionado con nombre o precio
        error_fields = {error['loc'][0] for error in errors}
        assert error_fields.intersection({'nombre', 'precio'}), \
            f"Expected validation error for 'nombre' or 'precio', got errors for: {error_fields}"
