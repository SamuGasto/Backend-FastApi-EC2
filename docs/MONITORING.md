# Guía de Monitoreo y Troubleshooting

## Comandos Útiles

### Ver logs en tiempo real

```bash
sudo journalctl -u fastapi -f
```

### Ver últimas 50 líneas

```bash
sudo journalctl -u fastapi -n 50
```

### Ver logs con errores

```bash
sudo journalctl -u fastapi | grep ERROR
```

### Estado del servicio

```bash
sudo systemctl status fastapi
```

### Reiniciar servicio

```bash
sudo systemctl restart fastapi
```

## Verificar Configuración

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python check_config.py
```

## Problemas Comunes

### 1. Timeout en `/productos`

**Síntoma:** `/health` funciona pero `/productos` da timeout

**Causa:** Security Group de RDS no permite conexiones desde EC2

**Solución:**

```bash
# Diagnosticar
python scripts/diagnose_db.py

# Arreglar Security Group
# AWS Console → RDS → Security Group → Edit inbound rules
# Add rule: PostgreSQL (5432) desde EC2 Security Group
```

### 2. Error "Could not parse SQLAlchemy URL"

**Síntoma:** Error al iniciar el servicio

**Causa:** DATABASE_URL mal formado en `.env`

**Solución:**

```bash
# Formato correcto
echo "DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require" > .env
sudo systemctl restart fastapi
```

### 3. Servicio no inicia

**Diagnóstico:**

```bash
# Ver error específico
sudo journalctl -u fastapi -n 20

# Verificar que el archivo existe
ls -la /etc/systemd/system/fastapi.service

# Verificar permisos
ls -la /home/ec2-user/Backend-FastApi-EC2/

# Probar manualmente
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. No se puede conectar a RDS

**Diagnóstico:**

```bash
# Probar conexión TCP
nc -zv rds-endpoint.amazonaws.com 5432

# Probar con psql
psql "$DATABASE_URL"

# Diagnosticar completo
python scripts/diagnose_db.py
```

**Soluciones:**

- Verificar Security Groups
- Verificar que RDS esté en estado "Available"
- Verificar credenciales en DATABASE_URL
- Verificar que EC2 tenga acceso a internet (para resolver DNS)

## Health Check

El endpoint `/health` verifica:

- Aplicación corriendo
- Conexión a base de datos

```bash
curl http://localhost:8000/health
```

Respuesta exitosa:

```json
{
  "status": "healthy",
  "service": "productos-api",
  "database": "connected"
}
```

Respuesta con error:

```json
{
  "status": "unhealthy",
  "service": "productos-api",
  "database": "disconnected",
  "error": "mensaje de error"
}
```

## Métricas de CloudWatch

Si usas Auto Scaling, monitorea:

- **CPUUtilization**: Uso de CPU
- **TargetResponseTime**: Tiempo de respuesta
- **HealthyHostCount**: Instancias saludables
- **UnHealthyHostCount**: Instancias con problemas
- **RequestCount**: Número de requests

## Logs de Aplicación

Los logs incluyen:

- Inicio de aplicación
- Conexiones a base de datos
- Requests HTTP
- Errores y excepciones

Formato:

```
2024-11-27 04:09:25,308 - app.main - INFO - FastAPI application initialized with PostgreSQL
```

## Backup y Recuperación

### Backup de RDS

AWS RDS hace backups automáticos. Para restaurar:

1. RDS Console → Snapshots
2. Selecciona snapshot → Restore
3. Actualiza DATABASE_URL en EC2

### Backup de código

El código está en Git. Para recuperar:

```bash
cd /home/ec2-user/Backend-FastApi-EC2
git pull origin main
sudo systemctl restart fastapi
```

## Alertas Recomendadas

Configura CloudWatch Alarms para:

- CPU > 80% por 5 minutos
- Unhealthy hosts > 0
- Target response time > 1 segundo
- RDS CPU > 80%
- RDS Free Storage < 10GB
