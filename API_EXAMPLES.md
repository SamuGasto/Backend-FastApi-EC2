# Ejemplos de Uso de la API 📝

Ejemplos prácticos para usar la API de productos.

## Configuración Base

```bash
# URL base (ajusta según tu entorno)
API_URL="http://localhost:8000"

# O si está en EC2
API_URL="http://tu-ip-ec2:8000"
```

## Endpoints Disponibles

### 1. Mensaje de Bienvenida

```bash
curl $API_URL/
```

**Respuesta:**

```json
{
  "message": "Bienvenido a la API de Productos"
}
```

### 2. Crear un Producto

```bash
curl -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell XPS 15",
    "precio": 1299.99,
    "descripcion": "Laptop de alto rendimiento con pantalla 4K"
  }'
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Laptop Dell XPS 15",
  "precio": 1299.99,
  "descripcion": "Laptop de alto rendimiento con pantalla 4K"
}
```

### 3. Listar Todos los Productos

```bash
curl $API_URL/productos
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Laptop Dell XPS 15",
    "precio": 1299.99,
    "descripcion": "Laptop de alto rendimiento con pantalla 4K"
  },
  {
    "id": 2,
    "nombre": "Mouse Logitech MX Master 3",
    "precio": 99.99,
    "descripcion": "Mouse ergonómico inalámbrico"
  }
]
```

### 4. Obtener un Producto Específico

```bash
curl $API_URL/productos/1
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Laptop Dell XPS 15",
  "precio": 1299.99,
  "descripcion": "Laptop de alto rendimiento con pantalla 4K"
}
```

### 5. Actualizar un Producto

```bash
curl -X PUT $API_URL/productos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell XPS 15 (Actualizado)",
    "precio": 1199.99,
    "descripcion": "Laptop en oferta especial"
  }'
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Laptop Dell XPS 15 (Actualizado)",
  "precio": 1199.99,
  "descripcion": "Laptop en oferta especial"
}
```

### 6. Eliminar un Producto

```bash
curl -X DELETE $API_URL/productos/1
```

**Respuesta:** Status 204 (sin contenido)

## Validaciones

### Producto sin nombre (error)

```bash
curl -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 99.99
  }'
```

**Respuesta (422):**

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "nombre"],
      "msg": "Field required",
      "input": { "precio": 99.99 }
    }
  ]
}
```

### Precio negativo (error)

```bash
curl -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto",
    "precio": -10.0
  }'
```

**Respuesta (422):**

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "precio"],
      "msg": "Input should be greater than 0",
      "input": -10.0
    }
  ]
}
```

### Nombre vacío (error)

```bash
curl -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "",
    "precio": 50.0
  }'
```

**Respuesta (422):**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "nombre"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

## Usando Python

```python
import requests

API_URL = "http://localhost:8000"

# Crear producto
producto = {
    "nombre": "Teclado Mecánico",
    "precio": 149.99,
    "descripcion": "Teclado RGB con switches Cherry MX"
}

response = requests.post(f"{API_URL}/productos", json=producto)
print(response.json())

# Listar productos
response = requests.get(f"{API_URL}/productos")
productos = response.json()
for p in productos:
    print(f"{p['id']}: {p['nombre']} - ${p['precio']}")
```

## Usando JavaScript (fetch)

```javascript
const API_URL = "http://localhost:8000";

// Crear producto
async function crearProducto() {
  const producto = {
    nombre: "Monitor 4K",
    precio: 599.99,
    descripcion: "Monitor 27 pulgadas 4K HDR",
  };

  const response = await fetch(`${API_URL}/productos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(producto),
  });

  const data = await response.json();
  console.log(data);
}

// Listar productos
async function listarProductos() {
  const response = await fetch(`${API_URL}/productos`);
  const productos = await response.json();

  productos.forEach((p) => {
    console.log(`${p.id}: ${p.nombre} - $${p.precio}`);
  });
}

crearProducto();
listarProductos();
```

## Documentación Interactiva

La forma más fácil de probar la API es usando la documentación interactiva:

**Swagger UI:** http://localhost:8000/docs

Aquí puedes:

- Ver todos los endpoints
- Probar cada endpoint directamente desde el navegador
- Ver los esquemas de datos
- Ver ejemplos de respuestas

**ReDoc:** http://localhost:8000/redoc

Documentación alternativa más limpia y fácil de leer.

## Script de Prueba Completo

Guarda esto como `test_api.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000"

echo "🧪 Probando API de Productos"
echo "=============================="
echo ""

# Test 1: Bienvenida
echo "1️⃣ Test: Mensaje de bienvenida"
curl -s $API_URL/ | jq
echo ""

# Test 2: Crear producto 1
echo "2️⃣ Test: Crear producto 1"
curl -s -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop", "precio": 999.99}' | jq
echo ""

# Test 3: Crear producto 2
echo "3️⃣ Test: Crear producto 2"
curl -s -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mouse", "precio": 29.99}' | jq
echo ""

# Test 4: Listar productos
echo "4️⃣ Test: Listar todos los productos"
curl -s $API_URL/productos | jq
echo ""

# Test 5: Error de validación
echo "5️⃣ Test: Error de validación (precio negativo)"
curl -s -X POST $API_URL/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Producto", "precio": -10}' | jq
echo ""

echo "✅ Tests completados!"
```

Ejecuta:

```bash
chmod +x test_api.sh
./test_api.sh
```

## Tips

- Usa `jq` para formatear JSON: `curl ... | jq`
- Usa `-v` en curl para ver headers: `curl -v ...`
- Usa Postman o Insomnia para pruebas más complejas
- La documentación en `/docs` es tu mejor amiga

## ¿Necesitas más ejemplos?

Revisa los tests en `tests/` para ver cómo se usa la API programáticamente.
