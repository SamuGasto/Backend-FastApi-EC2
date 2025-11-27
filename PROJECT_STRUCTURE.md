# Estructura del Proyecto

```
Backend-FastApi-EC2/
│
├── app/                          # Aplicación principal
│   ├── models/                   # Modelos de datos (SQLAlchemy + Pydantic)
│   │   └── product.py           # Modelo de Producto
│   ├── routes/                   # Endpoints de la API
│   │   └── products.py          # Rutas de productos
│   ├── config.py                # Configuración (variables de entorno)
│   ├── database.py              # Conexión a PostgreSQL
│   └── main.py                  # Aplicación FastAPI principal
│
├── tests/                        # Tests unitarios
│   ├── conftest.py              # Configuración de pytest
│   ├── test_config.py           # Tests de configuración
│   ├── test_models.py           # Tests de modelos
│   └── test_routes.py           # Tests de endpoints
│
├── scripts/                      # Scripts de utilidad
│   ├── test_api.sh              # Test completo de API
│   └── diagnose_db.py           # Diagnóstico de conexión a BD
│
├── docs/                         # Documentación adicional
│   ├── AUTOSCALING.md           # Guía de Auto Scaling y ALB
│   └── MONITORING.md            # Guía de monitoreo
│
├── .env                         # Variables de entorno (NO en git)
├── .env.example                 # Ejemplo de configuración
├── .gitignore                   # Archivos ignorados por git
│
├── requirements.txt             # Dependencias Python
├── setup.sh                     # Script de instalación
├── start.sh                     # Script para iniciar servidor local
├── deploy-ec2.sh               # Script de despliegue en EC2
│
├── check_config.py             # Verificar configuración
├── migrate_database.sql        # Migración de base de datos
│
├── fastapi.service             # Servicio systemd para EC2
├── gunicorn_config.py          # Configuración de Gunicorn
│
├── README.md                   # Documentación principal
├── QUICK_REFERENCE.md          # Referencia rápida
└── PROJECT_STRUCTURE.md        # Este archivo
```

## Archivos Clave

### Aplicación

- **app/main.py**: Punto de entrada de FastAPI
- **app/database.py**: Configuración de SQLAlchemy y pool de conexiones
- **app/models/product.py**: Modelo de Producto (BD y API)
- **app/routes/products.py**: Endpoints CRUD de productos

### Configuración

- **.env**: Variables de entorno (DATABASE_URL, APP_PORT, etc.)
- **app/config.py**: Carga variables de entorno
- **requirements.txt**: Dependencias Python

### Despliegue

- **deploy-ec2.sh**: Despliegue automatizado en EC2
- **fastapi.service**: Servicio systemd para producción
- **gunicorn_config.py**: Configuración de workers

### Testing

- **tests/**: Tests unitarios con pytest
- **scripts/test_api.sh**: Tests de integración de API
- **scripts/diagnose_db.py**: Diagnóstico de conexión

### Documentación

- **README.md**: Guía principal
- **QUICK_REFERENCE.md**: Comandos rápidos
- **docs/AUTOSCALING.md**: Configuración de AWS
- **docs/MONITORING.md**: Monitoreo y troubleshooting

## Flujo de Trabajo

### Desarrollo Local

1. `bash setup.sh` - Instalar dependencias
2. Configurar `.env` con DATABASE_URL
3. `python check_config.py` - Verificar configuración
4. `bash start.sh` - Iniciar servidor
5. `pytest -v` - Ejecutar tests

### Despliegue en EC2

1. `bash deploy-ec2.sh "DATABASE_URL"` - Despliegue automatizado
2. Verificar con `curl http://localhost:8000/health`
3. Monitorear con `sudo journalctl -u fastapi -f`

### Actualización

1. Hacer cambios en código
2. Commit y push a git
3. En EC2: `git pull && sudo systemctl restart fastapi`
4. Crear nueva AMI para Auto Scaling

## Dependencias Principales

- **FastAPI**: Framework web
- **SQLAlchemy**: ORM para PostgreSQL
- **Pydantic**: Validación de datos
- **psycopg2-binary**: Driver de PostgreSQL
- **python-dotenv**: Manejo de variables de entorno
- **uvicorn**: Servidor ASGI
- **gunicorn**: Servidor de producción
- **pytest**: Framework de testing
