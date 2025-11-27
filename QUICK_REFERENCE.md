# Referencia Rápida

## Comandos Esenciales

### Local

```bash
# Iniciar
bash start.sh

# Verificar configuración
python check_config.py

# Tests
pytest -v
```

### EC2

```bash
# Ver logs
sudo journalctl -u fastapi -f

# Reiniciar
sudo systemctl restart fastapi

# Estado
sudo systemctl status fastapi
```

## API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Listar productos
curl http://localhost:8000/productos

# Crear producto
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Laptop","descripcion":"HP 15","precio":899.99,"stock":10}'

# Obtener producto
curl http://localhost:8000/productos/1

# Actualizar producto
curl -X PUT http://localhost:8000/productos/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Laptop Pro","descripcion":"HP 15","precio":999.99,"stock":8}'

# Eliminar producto
curl -X DELETE http://localhost:8000/productos/1
```

## Troubleshooting

### Timeout en /productos

```bash
# Diagnosticar
python scripts/diagnose_db.py

# Solución: Arreglar Security Group de RDS
# AWS Console → RDS → Security Group → Add inbound rule
# Type: PostgreSQL (5432), Source: EC2 Security Group
```

### Error de DATABASE_URL

```bash
# Formato correcto
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Documentación Completa

- [README.md](README.md) - Guía principal
- [docs/AUTOSCALING.md](docs/AUTOSCALING.md) - Auto Scaling y ALB
- [docs/MONITORING.md](docs/MONITORING.md) - Monitoreo y troubleshooting
