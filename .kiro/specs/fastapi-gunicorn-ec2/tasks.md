# Plan de Implementación

- [x] 1. Configurar estructura del proyecto y archivos base

  - Crear estructura de directorios (app/, tests/, etc.)
  - Crear archivos **init**.py necesarios
  - Crear requirements.txt con dependencias
  - Crear .gitignore para Python
  - Crear .env.example con variables de entorno
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2_

- [x] 2. Implementar modelo de Producto con validación Pydantic

  - Crear app/models/product.py con clase Product
  - Definir campos: id, nombre, precio, descripcion
  - Configurar validaciones con Pydantic (min_length, gt)
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2.1 Escribir unit tests para modelo Producto

  - Test de campos obligatorios (nombre, precio)
  - Test de inicialización con datos válidos
  - _Requirements: 2.1, 2.3_

- [x] 2.2 Escribir property test para serialización round trip

  - **Property 1: Serialización round trip de Producto**
  - **Validates: Requirements 2.5**
  - Generar productos válidos aleatorios
  - Serializar a JSON y deserializar
  - Verificar equivalencia
  - _Requirements: 2.5_

- [x] 2.3 Escribir property test para rechazo de datos inválidos

  - **Property 4: Rechazo de datos inválidos**
  - **Validates: Requirements 2.2, 2.4, 3.4, 7.1**
  - Generar datos inválidos aleatorios
  - Verificar rechazo con error de validación
  - _Requirements: 2.2, 2.4_

- [x] 3. Implementar sistema de almacenamiento en memoria

  - Crear app/storage/memory.py con clase ProductStorage
  - Implementar método add() para agregar productos
  - Implementar método get_all() para listar productos
  - Implementar generación de IDs únicos
  - Inicializar almacenamiento vacío
  - _Requirements: 6.1, 6.2, 6.4_

- [x] 3.1 Escribir unit test para estado inicial

  - Verificar que almacenamiento inicia vacío
  - _Requirements: 6.4_

- [x] 3.2 Escribir property test para unicidad de identificadores

  - **Property 5: Unicidad de identificadores**
  - **Validates: Requirements 6.2, 6.5**
  - Crear múltiples productos aleatorios
  - Verificar que todos los IDs sean únicos
  - _Requirements: 6.2, 6.5_

- [x] 4. Crear aplicación FastAPI principal

  - Crear app/main.py con instancia de FastAPI
  - Configurar metadatos (title, description, version)
  - Configurar logging básico
  - _Requirements: 1.1, 7.4_

- [x] 5. Implementar endpoints REST para productos

  - Crear app/routes/products.py con APIRouter
  - Implementar endpoint GET / (mensaje de bienvenida) en main.py
  - Implementar endpoint POST /productos (crear producto)
  - Implementar endpoint GET /productos (listar productos)
  - Integrar router en aplicación principal
  - Conectar endpoints con ProductStorage
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 5.1 Escribir unit tests para endpoints específicos

  - Test de endpoint raíz (/) retorna mensaje de bienvenida
  - Test de endpoint /docs está disponible
  - Test de endpoint inexistente retorna 404
  - _Requirements: 3.1, 3.5, 7.2_

- [x] 5.2 Escribir property test para creación de productos válidos

  - **Property 2: Creación de productos válidos**
  - **Validates: Requirements 3.2**
  - Generar datos válidos aleatorios
  - Crear producto via POST
  - Verificar que se retorna con ID asignado
  - _Requirements: 3.2_

- [x] 5.3 Escribir property test para listado completo

  - **Property 3: Listado completo de productos**
  - **Validates: Requirements 3.3, 6.1, 6.3**
  - Crear cantidad aleatoria de productos
  - Listar todos via GET
  - Verificar que todos estén presentes
  - _Requirements: 3.3, 6.1, 6.3_

- [x] 5.4 Escribir property test para validación de entrada en endpoints

  - **Property 4: Rechazo de datos inválidos** (validación en API)
  - **Validates: Requirements 2.4, 3.4, 7.1**
  - Generar datos inválidos aleatorios
  - Intentar POST con datos inválidos
  - Verificar HTTP 422 con mensaje descriptivo
  - _Requirements: 3.4, 7.1_

- [x] 6. Checkpoint - Verificar que todos los tests pasen

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6.1 Escribir property test para estabilidad después de errores

  - **Property 6: Estabilidad después de errores**
  - **Validates: Requirements 7.5**
  - Generar secuencia aleatoria de operaciones válidas e inválidas
  - Verificar que operaciones válidas sigan funcionando
  - _Requirements: 7.5_

- [x] 6.2 Escribir unit test para error interno

  - Test de error interno retorna 500
  - _Requirements: 7.3_

- [x] 7. Configurar Gunicorn para producción

  - Crear gunicorn_config.py con configuración
  - Configurar bind (0.0.0.0:8000)
  - Configurar workers (4)
  - Configurar worker_class (uvicorn.workers.UvicornWorker)
  - Configurar timeout (120)
  - Crear start.sh script de inicio
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 8. Crear documentación y archivos de configuración

  - Crear README.md con instrucciones de instalación
  - Documentar cómo ejecutar localmente
  - Documentar cómo clonar y configurar el proyecto
  - Documentar instrucciones de despliegue en EC2
  - Incluir comandos para configurar Security Group
  - _Requirements: 1.5, 5.3, 5.4, 5.5_

- [x] 9. Checkpoint final - Verificar proyecto completo

  - Ensure all tests pass, ask the user if questions arise.
