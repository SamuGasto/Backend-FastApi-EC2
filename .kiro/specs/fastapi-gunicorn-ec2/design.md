# Documento de Diseño

## Overview

Esta aplicación es una API REST básica construida con FastAPI que gestiona un inventario simple de productos de tienda. La aplicación utiliza Gunicorn como servidor WSGI para producción y está diseñada para desplegarse en una instancia EC2 de AWS. El almacenamiento es en memoria, manteniendo la simplicidad del proyecto como prueba de concepto.

## Architecture

La aplicación sigue una arquitectura de tres capas simplificada:

```
┌─────────────────────────────────────┐
│         Cliente HTTP                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Gunicorn (Servidor WSGI)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌─────────────────────────────┐   │
│  │    Endpoints (Rutas)        │   │
│  └────────────┬────────────────┘   │
│               │                     │
│               ▼                     │
│  ┌─────────────────────────────┐   │
│  │    Modelos Pydantic         │   │
│  └────────────┬────────────────┘   │
│               │                     │
│               ▼                     │
│  ┌─────────────────────────────┐   │
│  │  Almacenamiento en Memoria  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Componentes principales:**

- **FastAPI App**: Aplicación principal que maneja las rutas y validación
- **Modelos Pydantic**: Definición y validación de datos de Producto
- **Almacenamiento en Memoria**: Diccionario Python simple para persistencia temporal
- **Gunicorn**: Servidor de producción con múltiples workers

## Components and Interfaces

### 1. Aplicación Principal (main.py)

```python
from fastapi import FastAPI

app = FastAPI(
    title="API de Productos",
    description="API básica para gestión de productos de tienda",
    version="1.0.0"
)
```

**Responsabilidades:**

- Inicializar la aplicación FastAPI
- Configurar metadatos de la API
- Registrar rutas y middleware

### 2. Modelo de Producto (models/product.py)

```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    id: Optional[int] = None
    nombre: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    descripcion: Optional[str] = None
```

**Responsabilidades:**

- Definir estructura de datos del Producto
- Validar tipos y restricciones de campos
- Serialización/deserialización JSON

### 3. Rutas de Productos (routes/products.py)

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/productos", tags=["productos"])

@router.get("/")
async def list_products()

@router.post("/")
async def create_product(product: Product)
```

**Responsabilidades:**

- Definir endpoints REST
- Manejar peticiones HTTP
- Validar entrada y retornar respuestas

### 4. Almacenamiento (storage/memory.py)

```python
class ProductStorage:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.next_id: int = 1

    def add(self, product: Product) -> Product
    def get_all(self) -> List[Product]
```

**Responsabilidades:**

- Gestionar productos en memoria
- Generar IDs únicos
- Operaciones CRUD básicas

### 5. Configuración de Gunicorn (gunicorn_config.py)

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
```

**Responsabilidades:**

- Configurar workers y binding
- Definir timeouts
- Especificar worker class para ASGI

## Data Models

### Product

| Campo       | Tipo  | Obligatorio | Validación    | Descripción          |
| ----------- | ----- | ----------- | ------------- | -------------------- |
| id          | int   | No          | Auto-generado | Identificador único  |
| nombre      | str   | Sí          | min_length=1  | Nombre del producto  |
| precio      | float | Sí          | > 0           | Precio del producto  |
| descripcion | str   | No          | -             | Descripción opcional |

**Ejemplo JSON:**

```json
{
  "id": 1,
  "nombre": "Laptop",
  "precio": 999.99,
  "descripcion": "Laptop de alta gama"
}
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Serialización round trip de Producto

_Para cualquier_ Producto válido, serializarlo a JSON y luego deserializarlo debe producir un objeto equivalente
**Validates: Requirements 2.5**

### Property 2: Creación de productos válidos

_Para cualquier_ conjunto de datos válidos de producto (nombre no vacío, precio positivo), crear un Producto mediante POST debe retornar el objeto creado con un ID asignado
**Validates: Requirements 3.2**

### Property 3: Listado completo de productos

_Para cualquier_ conjunto de productos creados, una petición GET a /productos debe retornar todos los productos almacenados
**Validates: Requirements 3.3, 6.1, 6.3**

### Property 4: Rechazo de datos inválidos

_Para cualquier_ dato inválido (nombre vacío, precio negativo o cero, tipos incorrectos), el sistema debe rechazar la creación y retornar HTTP 422 con mensaje descriptivo del error
**Validates: Requirements 2.2, 2.4, 3.4, 7.1**

### Property 5: Unicidad de identificadores

_Para cualquier_ conjunto de productos creados, todos los IDs asignados deben ser únicos y no debe haber conflictos
**Validates: Requirements 6.2, 6.5**

### Property 6: Estabilidad después de errores

_Para cualquier_ secuencia de operaciones que incluya errores de validación, el sistema debe mantener su funcionalidad y seguir procesando peticiones válidas correctamente
**Validates: Requirements 7.5**

## Error Handling

La aplicación implementa un manejo de errores en múltiples niveles:

### 1. Validación de Pydantic

- FastAPI automáticamente valida los datos de entrada usando los modelos Pydantic
- Retorna HTTP 422 con detalles específicos de los campos inválidos
- Ejemplo de respuesta de error:

```json
{
  "detail": [
    {
      "loc": ["body", "precio"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 2. Errores de Ruta

- FastAPI maneja automáticamente rutas no encontradas con HTTP 404
- Respuesta estándar para endpoints inexistentes

### 3. Errores Internos

- Excepciones no capturadas retornan HTTP 500
- Se registran en logs para diagnóstico
- El servidor Gunicorn mantiene la estabilidad reiniciando workers si es necesario

### 4. Logging

- Configuración básica de logging de Python
- Registro de errores y excepciones
- Logs accesibles para debugging en EC2

## Testing Strategy

### Unit Testing

Utilizaremos **pytest** como framework de testing. Los unit tests cubrirán:

1. **Validación del modelo Producto**

   - Verificar que campos obligatorios (nombre, precio) sean requeridos
   - Verificar que el modelo se inicialice correctamente con datos válidos

2. **Endpoints específicos**

   - Test del endpoint raíz (/) retorna mensaje de bienvenida
   - Test del endpoint de documentación (/docs) está disponible
   - Test de endpoint inexistente retorna 404

3. **Estado inicial**

   - Verificar que el almacenamiento inicia vacío

4. **Casos de error específicos**
   - Test de error interno retorna 500

### Property-Based Testing

Utilizaremos **Hypothesis** como biblioteca de property-based testing para Python. Configuración:

- Mínimo 100 iteraciones por propiedad
- Cada test debe referenciar explícitamente la propiedad del diseño

Los property tests cubrirán:

1. **Property 1: Serialización round trip**

   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 1: Serialización round trip de Producto**`
   - Generar productos aleatorios válidos
   - Serializar a JSON y deserializar
   - Verificar equivalencia

2. **Property 2: Creación de productos válidos**

   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 2: Creación de productos válidos**`
   - Generar datos válidos aleatorios
   - Crear producto via POST
   - Verificar que se retorna con ID

3. **Property 3: Listado completo**

   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 3: Listado completo de productos**`
   - Crear cantidad aleatoria de productos
   - Listar todos
   - Verificar que todos estén presentes

4. **Property 4: Rechazo de datos inválidos**

   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 4: Rechazo de datos inválidos**`
   - Generar datos inválidos aleatorios
   - Intentar crear producto
   - Verificar HTTP 422 y mensaje de error

5. **Property 5: Unicidad de identificadores**

   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 5: Unicidad de identificadores**`
   - Crear múltiples productos aleatorios
   - Verificar que todos los IDs sean únicos

6. **Property 6: Estabilidad después de errores**
   - Tag: `**Feature: fastapi-gunicorn-ec2, Property 6: Estabilidad después de errores**`
   - Generar secuencia aleatoria de operaciones válidas e inválidas
   - Verificar que operaciones válidas sigan funcionando

## Deployment Considerations

### Estructura del Proyecto

```
fastapi-gunicorn-ec2/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── products.py
│   └── storage/
│       ├── __init__.py
│       └── memory.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_routes.py
│   └── test_properties.py
├── gunicorn_config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── start.sh
```

### Dependencias (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.5.0
pytest==7.4.3
hypothesis==6.92.1
httpx==0.25.2
```

### Variables de Entorno (.env.example)

```
APP_HOST=0.0.0.0
APP_PORT=8000
WORKERS=4
LOG_LEVEL=info
```

### Script de Inicio (start.sh)

```bash
#!/bin/bash
gunicorn -c gunicorn_config.py app.main:app
```

### Instrucciones de Despliegue en EC2

1. **Conectar a EC2:**

   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

2. **Instalar Python y dependencias:**

   ```bash
   sudo yum update -y
   sudo yum install python3 python3-pip git -y
   ```

3. **Clonar repositorio:**

   ```bash
   git clone <your-repo-url>
   cd fastapi-gunicorn-ec2
   ```

4. **Crear entorno virtual e instalar dependencias:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configurar variables de entorno:**

   ```bash
   cp .env.example .env
   # Editar .env según necesidades
   ```

6. **Ejecutar aplicación:**

   ```bash
   chmod +x start.sh
   ./start.sh
   ```

7. **Configurar como servicio systemd (opcional):**
   Crear `/etc/systemd/system/fastapi.service`:

   ```ini
   [Unit]
   Description=FastAPI Application
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/fastapi-gunicorn-ec2
   Environment="PATH=/home/ec2-user/fastapi-gunicorn-ec2/venv/bin"
   ExecStart=/home/ec2-user/fastapi-gunicorn-ec2/start.sh

   [Install]
   WantedBy=multi-user.target
   ```

   Luego:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fastapi
   sudo systemctl start fastapi
   ```

### Configuración de Security Group en EC2

- Abrir puerto 8000 para tráfico HTTP
- Configurar reglas de entrada apropiadas según necesidades de seguridad

### Monitoreo

- Logs de Gunicorn disponibles en stdout/stderr
- Considerar usar CloudWatch para monitoreo en producción
- Verificar salud de la aplicación: `curl http://localhost:8000/`
