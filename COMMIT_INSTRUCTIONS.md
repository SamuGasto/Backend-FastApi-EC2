# Instrucciones para Commit

## Resumen de Cambios

Este commit incluye:

- ✅ Limpieza y organización del proyecto
- ✅ Agregado campo `stock` al modelo de Producto
- ✅ Mejoras en conexión a base de datos (timeouts, pool)
- ✅ Documentación consolidada y simplificada
- ✅ Estructura de carpetas más profesional

## Comandos para Commit

```bash
# Ver cambios
git status

# Agregar todos los cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat: Reorganización del proyecto y mejoras en BD

- Agregado campo stock al modelo de Producto
- Configurados timeouts y pool de conexiones a PostgreSQL
- Reorganizada documentación en carpeta docs/
- Movidos scripts de utilidad a carpeta scripts/
- Eliminados archivos redundantes y temporales
- Actualizado README con documentación consolidada
- Agregadas guías de referencia rápida"

# Push a repositorio
git push origin main
```

## Después del Commit

### 1. Actualizar EC2 Actual

```bash
# Conectar a EC2
ssh ec2-user@TU_IP_EC2

# Ir al proyecto
cd /home/ec2-user/Backend-FastApi-EC2

# Actualizar código
git pull origin main

# Migrar base de datos (agregar campo stock)
source .env
psql "$DATABASE_URL" -f migrate_database.sql

# Reiniciar servicio
sudo systemctl restart fastapi

# Verificar
curl http://localhost:8000/health
curl http://localhost:8000/productos
```

### 2. Probar Nuevo Campo Stock

```bash
# Crear producto con stock
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop HP",
    "descripcion": "Laptop 15 pulgadas",
    "precio": 899.99,
    "stock": 10
  }'

# Verificar
curl http://localhost:8000/productos
```

### 3. Crear Nueva AMI (Opcional)

Si usas Auto Scaling:

1. AWS Console → EC2 → Instances
2. Selecciona tu instancia
3. Actions → Image and templates → Create image
4. Name: `productos-api-v2`
5. Description: `Con campo stock y mejoras en BD`

### 4. Actualizar Auto Scaling Group (Opcional)

Si tienes ASG configurado:

1. Actualizar Launch Template con nueva AMI
2. Hacer Instance Refresh del ASG

## Verificación Final

Asegúrate de que todo funcione:

```bash
# Health check
curl http://TU_URL/health
# Debe retornar: {"status":"healthy","service":"productos-api","database":"connected"}

# Listar productos
curl http://TU_URL/productos
# Debe retornar: [] o lista de productos

# Crear producto
curl -X POST http://TU_URL/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","descripcion":"Prueba","precio":99.99,"stock":5}'
# Debe retornar: el producto creado con ID

# Documentación
# Abrir en navegador: http://TU_URL/docs
```

## Archivos Importantes Modificados

### Código

- `app/database.py` - Timeouts y pool configurados
- `app/models/product.py` - Campo stock agregado
- `app/routes/products.py` - Soporte para stock

### Documentación

- `README.md` - Documentación principal actualizada
- `docs/AUTOSCALING.md` - Guía de Auto Scaling
- `docs/MONITORING.md` - Guía de monitoreo
- `QUICK_REFERENCE.md` - Referencia rápida

### Scripts

- `scripts/test_api.sh` - Tests de API
- `scripts/diagnose_db.py` - Diagnóstico de BD

### Configuración

- `.env.example` - Ejemplo actualizado
- `.gitignore` - Exclusiones actualizadas
- `migrate_database.sql` - Migración de BD

## Notas

- El archivo `.env` NO se sube a git (está en .gitignore)
- La carpeta `.hypothesis/` es generada por tests y está en .gitignore
- Los archivos `__pycache__/` son generados automáticamente
- El archivo `test.db` fue eliminado (era temporal)

## Soporte

Si tienes problemas después del commit:

1. Revisa `docs/MONITORING.md` para troubleshooting
2. Ejecuta `python scripts/diagnose_db.py` para diagnosticar BD
3. Revisa logs con `sudo journalctl -u fastapi -n 50`
