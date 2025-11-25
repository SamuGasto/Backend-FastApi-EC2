"""
Unit tests para endpoints específicos de la API.
Tests de endpoints raíz, documentación y manejo de rutas inexistentes.
Requirements: 3.1, 3.5, 7.2
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck


class TestEndpoints:
    """Tests para endpoints específicos de la API"""
    
    def test_root_endpoint_returns_welcome_message(self, client):
        """
        Test de endpoint raíz (/) retorna mensaje de bienvenida.
        Requirements: 3.1
        """
        response = client.get("/")
        
        # Verificar código de estado exitoso
        assert response.status_code == 200
        
        # Verificar que retorna JSON
        assert response.headers["content-type"] == "application/json"
        
        # Verificar estructura de respuesta
        data = response.json()
        assert "message" in data
        
        # Verificar mensaje de bienvenida
        assert data["message"] == "Bienvenido a la API de Productos"
    
    def test_docs_endpoint_is_available(self, client):
        """
        Test de endpoint /docs está disponible.
        Requirements: 3.5
        """
        response = client.get("/docs")
        
        # Verificar que el endpoint de documentación está disponible
        assert response.status_code == 200
        
        # Verificar que retorna HTML (la interfaz de Swagger UI)
        assert "text/html" in response.headers["content-type"]
        
        # Verificar que contiene elementos de Swagger UI
        assert "swagger-ui" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_nonexistent_endpoint_returns_404(self, client):
        """
        Test de endpoint inexistente retorna 404.
        Requirements: 7.2
        """
        response = client.get("/ruta/inexistente")
        
        # Verificar código de estado 404
        assert response.status_code == 404
        
        # Verificar que retorna JSON con detalle del error
        data = response.json()
        assert "detail" in data


class TestProductEndpointsProperties:
    """Property-based tests para endpoints de productos"""
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        nombre=st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
        precio=st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        descripcion=st.one_of(st.none(), st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), max_size=500))
    )
    def test_create_product_with_valid_data(self, client, nombre, precio, descripcion):
        """
        **Feature: fastapi-gunicorn-ec2, Property 2: Creación de productos válidos**
        **Validates: Requirements 3.2**
        
        Para cualquier conjunto de datos válidos de producto (nombre no vacío, precio positivo),
        crear un Producto mediante POST debe retornar el objeto creado con un ID asignado.
        """
        # Preparar datos del producto
        product_data = {
            "nombre": nombre,
            "precio": precio
        }
        
        # Incluir descripción solo si no es None
        if descripcion is not None:
            product_data["descripcion"] = descripcion
        
        # Crear producto via POST
        response = client.post("/productos/", json=product_data)
        
        # Verificar código de estado 201 (Created)
        assert response.status_code == 201, \
            f"Expected status 201, got {response.status_code}. Response: {response.text}"
        
        # Verificar que retorna JSON
        assert response.headers["content-type"] == "application/json"
        
        # Obtener datos de respuesta
        created_product = response.json()
        
        # Verificar que se retorna con ID asignado
        assert "id" in created_product, "Product should have an 'id' field"
        assert created_product["id"] is not None, "Product ID should not be None"
        assert isinstance(created_product["id"], int), "Product ID should be an integer"
        assert created_product["id"] > 0, "Product ID should be positive"
        
        # Verificar que los datos del producto coinciden
        assert created_product["nombre"] == nombre, "Product name should match input"
        assert created_product["precio"] == precio, "Product price should match input"
        
        # Verificar descripción
        if descripcion is not None:
            assert created_product["descripcion"] == descripcion, "Product description should match input"
        else:
            assert created_product["descripcion"] is None, "Product description should be None when not provided"
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_products=st.integers(min_value=1, max_value=20)
    )
    def test_list_all_products(self, client, num_products):
        """
        **Feature: fastapi-gunicorn-ec2, Property 3: Listado completo de productos**
        **Validates: Requirements 3.3, 6.1, 6.3**
        
        Para cualquier conjunto de productos creados, una petición GET a /productos 
        debe retornar todos los productos almacenados.
        """
        
        # Crear cantidad aleatoria de productos
        created_products = []
        for i in range(num_products):
            product_data = {
                "nombre": f"Producto_Test_{i}",
                "precio": float(i + 1) * 10.5,
                "descripcion": f"Descripción del producto {i}"
            }
            
            # Crear producto via POST
            response = client.post("/productos/", json=product_data)
            assert response.status_code == 201, \
                f"Failed to create product {i}: {response.text}"
            
            created_product = response.json()
            created_products.append(created_product)
        
        # Listar todos los productos via GET
        response = client.get("/productos/")
        
        # Verificar código de estado exitoso
        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}. Response: {response.text}"
        
        # Obtener lista de productos
        listed_products = response.json()
        
        # Verificar que todos los productos creados están presentes
        assert len(listed_products) == num_products, \
            f"Expected {num_products} products, got {len(listed_products)}"
        
        # Verificar que cada producto creado está en la lista
        created_ids = {p["id"] for p in created_products}
        listed_ids = {p["id"] for p in listed_products}
        
        assert created_ids == listed_ids, \
            f"Product IDs don't match. Created: {created_ids}, Listed: {listed_ids}"
        
        # Verificar que los datos de cada producto coinciden
        listed_by_id = {p["id"]: p for p in listed_products}
        for created in created_products:
            listed = listed_by_id[created["id"]]
            assert listed["nombre"] == created["nombre"], \
                f"Product {created['id']} name mismatch"
            assert listed["precio"] == created["precio"], \
                f"Product {created['id']} price mismatch"
            assert listed["descripcion"] == created["descripcion"], \
                f"Product {created['id']} description mismatch"
    
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
            # Caso 4: tipo incorrecto para nombre (número) - viola tipo str
            st.fixed_dictionaries({
                'nombre': st.integers(),
                'precio': st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
            }),
            # Caso 5: tipo incorrecto para precio (string no numérico) - viola tipo float
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                'precio': st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10)
            }),
            # Caso 6: nombre faltante - viola campo obligatorio
            st.fixed_dictionaries({
                'precio': st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
            }),
            # Caso 7: precio faltante - viola campo obligatorio
            st.fixed_dictionaries({
                'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100)
            })
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_api_rejects_invalid_data_with_422(self, client, data):
        """
        **Feature: fastapi-gunicorn-ec2, Property 4: Rechazo de datos inválidos**
        **Validates: Requirements 2.4, 3.4, 7.1**
        
        Para cualquier dato inválido (nombre vacío, precio negativo o cero, tipos incorrectos),
        el sistema debe rechazar la creación mediante POST y retornar HTTP 422 con mensaje 
        descriptivo del error.
        """
        # Intentar POST con datos inválidos
        response = client.post("/productos/", json=data)
        
        # Verificar HTTP 422 (Unprocessable Entity)
        assert response.status_code == 422, \
            f"Expected status 422 for invalid data {data}, got {response.status_code}. Response: {response.text}"
        
        # Verificar que retorna JSON
        assert response.headers["content-type"] == "application/json"
        
        # Obtener detalles del error
        error_response = response.json()
        
        # Verificar que contiene campo 'detail' con información del error
        assert "detail" in error_response, \
            f"Response should contain 'detail' field. Got: {error_response}"
        
        # Verificar que detail es una lista de errores (formato estándar de FastAPI/Pydantic)
        assert isinstance(error_response["detail"], list), \
            f"'detail' should be a list of errors. Got: {type(error_response['detail'])}"
        
        # Verificar que hay al menos un error
        assert len(error_response["detail"]) > 0, \
            "Should have at least one validation error"
        
        # Verificar que cada error tiene la estructura esperada
        for error in error_response["detail"]:
            assert "loc" in error, "Each error should have 'loc' field"
            assert "msg" in error, "Each error should have 'msg' field (mensaje descriptivo)"
            assert "type" in error, "Each error should have 'type' field"
        
        # Verificar que el error está relacionado con nombre o precio
        error_fields = set()
        for error in error_response["detail"]:
            # loc es una tupla/lista como ['body', 'nombre'] o ['body', 'precio']
            if len(error["loc"]) >= 2:
                error_fields.add(error["loc"][1])
            elif len(error["loc"]) == 1:
                error_fields.add(error["loc"][0])
        
        assert error_fields.intersection({'nombre', 'precio'}), \
            f"Expected validation error for 'nombre' or 'precio', got errors for: {error_fields}"
    
    @given(
        operations=st.lists(
            st.one_of(
                # Operación válida: crear producto válido
                st.fixed_dictionaries({
                    'type': st.just('valid'),
                    'nombre': st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100),
                    'precio': st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False),
                    'descripcion': st.one_of(st.none(), st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), max_size=500))
                }),
                # Operación inválida: datos incorrectos
                st.fixed_dictionaries({
                    'type': st.just('invalid'),
                    'data': st.one_of(
                        st.fixed_dictionaries({'nombre': st.just(''), 'precio': st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)}),
                        st.fixed_dictionaries({'nombre': st.text(min_size=1, max_size=50), 'precio': st.just(0.0)}),
                        st.fixed_dictionaries({'nombre': st.text(min_size=1, max_size=50), 'precio': st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False)}),
                        st.fixed_dictionaries({'precio': st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)})
                    )
                })
            ),
            min_size=5,
            max_size=30
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_stability_after_errors(self, client, operations):
        """
        **Feature: fastapi-gunicorn-ec2, Property 6: Estabilidad después de errores**
        **Validates: Requirements 7.5**
        
        Para cualquier secuencia de operaciones que incluya errores de validación,
        el sistema debe mantener su funcionalidad y seguir procesando peticiones 
        válidas correctamente.
        """
        
        valid_products_created = []
        
        # Ejecutar secuencia de operaciones
        for operation in operations:
            if operation['type'] == 'valid':
                # Operación válida: debe funcionar correctamente
                product_data = {
                    'nombre': operation['nombre'],
                    'precio': operation['precio']
                }
                if operation['descripcion'] is not None:
                    product_data['descripcion'] = operation['descripcion']
                
                response = client.post("/productos/", json=product_data)
                
                # Verificar que la operación válida funciona después de errores previos
                assert response.status_code == 201, \
                    f"Valid operation failed after errors. Status: {response.status_code}, Response: {response.text}"
                
                created_product = response.json()
                assert 'id' in created_product
                assert created_product['id'] is not None
                valid_products_created.append(created_product)
                
            else:  # operation['type'] == 'invalid'
                # Operación inválida: debe fallar con 422
                response = client.post("/productos/", json=operation['data'])
                
                # Verificar que la operación inválida falla apropiadamente
                assert response.status_code == 422, \
                    f"Invalid operation should return 422, got {response.status_code}"
        
        # Verificar que el sistema sigue funcionando correctamente
        # Listar todos los productos debe retornar solo los válidos creados
        response = client.get("/productos/")
        assert response.status_code == 200, \
            f"System unstable after errors. GET failed with status {response.status_code}"
        
        listed_products = response.json()
        assert len(listed_products) == len(valid_products_created), \
            f"Expected {len(valid_products_created)} products, got {len(listed_products)}"
        
        # Verificar que podemos crear un nuevo producto válido después de toda la secuencia
        final_test_product = {
            'nombre': 'Test_Final_Product',
            'precio': 99.99
        }
        response = client.post("/productos/", json=final_test_product)
        assert response.status_code == 201, \
            f"System unable to create valid product after error sequence. Status: {response.status_code}"
