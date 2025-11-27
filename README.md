# API de Productos - FastAPI + PostgreSQL + AWS

API REST para gestión de productos con FastAPI, PostgreSQL (RDS) y despliegue en AWS EC2.

## 🚀 Quick Start

### Local

```bash
# 1. Clonar e instalar
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd Backend-FastApi-EC2
bash setup.sh

# 2. Configurar base de datos
cp .env.example .env
# Edita .env con tu DATABASE_URL

# 3. Verificar configuración
source venv/bin/activate
python check_config.py

# 4. Iniciar servidor
bash start.sh
```

Abre: http://localhost:8000/docs

### EC2 (Despliegue Automatizado)

```bash
# En tu instancia EC2
curl -O https://raw.githubusercontent.com/SamuGasto/Backend-FastApi-EC2/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh "postgresql://user:pass@rds-endpoint:5432/db?sslmode=require"
```

## 📦 API Endpoints

| Método | Endpoint          | Descripción         |
| ------ | ----------------- | ------------------- |
| GET    | `/health`         | Health check        |
| GET    | `/productos`      | Listar productos    |
| POST   | `/productos`      | Crear producto      |
| GET    | `/productos/{id}` | Obtener producto    |
| PUT    | `/productos/{id}` | Actualizar producto |
| DELETE | `/productos/{id}` | Eliminar producto   |

### Ejemplos

```bash
# Crear producto
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop HP",
    "descripcion": "Laptop 15 pulgadas",
    "precio": 899.99,
    "stock": 10
  }'

# Listar productos
curl http://localhost:8000/productos

# Health check
curl http://localhost:8000/health
```

## 🗄️ Configuración de Base de Datos

### RDS PostgreSQL

1. Crear instancia RDS PostgreSQL en AWS
2. Configurar Security Group:
   - **Inbound**: PostgreSQL (5432) desde Security Group de EC2
3. Obtener endpoint de conexión
4. Configurar `.env`:

```bash
DATABASE_URL=postgresql://admin:password@rds-endpoint.amazonaws.com:5432/postgres?sslmode=require
APP_PORT=8000
```

**Importante:** RDS requiere `?sslmode=require` al final del URL.

### Migración de Base de Datos

Si actualizas el esquema:

```bash
psql "$DATABASE_URL" -f migrate_database.sql
```

## 🔧 Despliegue en AWS

### Arquitectura Recomendada

```
Internet → ALB → Auto Scaling Group (EC2) → RDS PostgreSQL
```

### Pasos

1. **Crear AMI** desde EC2 funcionando
2. **Crear Launch Template** con la AMI
3. **Crear Target Group** con health check en `/health`
4. **Crear Application Load Balancer**
5. **Crear Auto Scaling Group** (2-10 instancias)

Ver guía completa: [docs/AUTOSCALING.md](docs/AUTOSCALING.md)

## 🧪 Testing

```bash
# Tests unitarios
pytest -v

# Test de API completo
bash scripts/test_api.sh http://localhost:8000
```

## 📊 Monitoreo

```bash
# Ver logs en tiempo real
sudo journalctl -u fastapi -f

# Estado del servicio
sudo systemctl status fastapi

# Reiniciar servicio
sudo systemctl restart fastapi
```

## 🛠️ Scripts Útiles

| Script                   | Descripción                    |
| ------------------------ | ------------------------------ |
| `setup.sh`               | Instalación inicial            |
| `start.sh`               | Iniciar servidor local         |
| `check_config.py`        | Verificar configuración        |
| `scripts/test_api.sh`    | Pruebas completas de API       |
| `scripts/diagnose_db.py` | Diagnosticar conexión a BD     |
| `deploy-ec2.sh`          | Despliegue automatizado en EC2 |

## 🔍 Troubleshooting

### Timeout en `/productos`

**Causa:** Security Group de RDS no permite conexiones desde EC2

**Solución:**

1. AWS Console → RDS → Tu instancia → Security Group
2. Edit inbound rules → Add rule:
   - Type: PostgreSQL (5432)
   - Source: Security Group de EC2

### Error "Could not parse SQLAlchemy URL"

**Causa:** DATABASE_URL mal formado

**Solución:**

```bash
# Formato correcto
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### Diagnosticar problemas de conexión

```bash
python scripts/diagnose_db.py
```

## 📁 Estructura del Proyecto

```
.
├── app/
│   ├── models/          # Modelos de datos
│   ├── routes/          # Endpoints de la API
│   ├── config.py        # Configuración
│   ├── database.py      # Conexión a BD
│   └── main.py          # Aplicación principal
├── tests/               # Tests unitarios
├── scripts/             # Scripts de utilidad
├── docs/                # Documentación adicional
├── requirements.txt     # Dependencias Python
├── setup.sh            # Script de instalación
├── deploy-ec2.sh       # Script de despliegue
└── fastapi.service     # Servicio systemd
```

## 🔐 Security Groups

### EC2 Security Group

- **Inbound**: HTTP (8000) desde ALB o 0.0.0.0/0
- **Inbound**: SSH (22) desde tu IP
- **Outbound**: All traffic

### RDS Security Group

- **Inbound**: PostgreSQL (5432) desde EC2 Security Group
- **Outbound**: All traffic

## 📝 Variables de Entorno

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require  # Requerido
APP_PORT=8000                                                       # Opcional (default: 8000)
WORKERS=4                                                           # Opcional (default: 4)
LOG_LEVEL=info                                                      # Opcional (default: info)
```

## 🚦 Health Check

El endpoint `/health` verifica:

- ✅ Aplicación corriendo
- ✅ Conexión a base de datos

Respuesta exitosa:

```json
{
  "status": "healthy",
  "service": "productos-api",
  "database": "connected"
}
```

## 📚 Documentación Adicional

- [Guía de Auto Scaling](docs/AUTOSCALING.md) - Configuración de ALB y ASG
- [Guía de Monitoreo](docs/MONITORING.md) - Logs y troubleshooting

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

MIT

---

Hecho con ❤️ usando FastAPI y AWS
