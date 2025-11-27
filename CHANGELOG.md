# Changelog

## [2024-11-27] - Limpieza y Organización del Proyecto

### ✅ Agregado

- Campo `stock` al modelo de Producto
- Timeouts de conexión a base de datos (10s connect, 30s query)
- Pool de conexiones configurado (5 base, 10 overflow)
- `pool_pre_ping` para verificar conexiones antes de usar
- Carpeta `docs/` para documentación extensa
- Carpeta `scripts/` para scripts de utilidad
- `QUICK_REFERENCE.md` - Referencia rápida de comandos
- `PROJECT_STRUCTURE.md` - Estructura del proyecto
- `docs/AUTOSCALING.md` - Guía consolidada de Auto Scaling
- `docs/MONITORING.md` - Guía consolidada de monitoreo

### 🔄 Movido

- `test_api.sh` → `scripts/test_api.sh`
- `diagnose_db.py` → `scripts/diagnose_db.py`
- Documentación extensa → `docs/`

### 🗑️ Eliminado

- `AUTOSCALING_SETUP.md` (consolidado en docs/)
- `MONITORING.md` (consolidado en docs/)
- `SOLUCION_TIMEOUT.md` (consolidado en docs/)
- `comandos_prueba.md` (consolidado en README)
- `GUIA_RAPIDA_API.md` (consolidado en README)
- `update_deployment.sh` (redundante)
- `test.db` (archivo temporal)
- `app/storage/` (carpeta vacía no utilizada)

### 📝 Actualizado

- `README.md` - Documentación principal consolidada y simplificada
- `.env.example` - Formato más claro con comentarios
- `.gitignore` - Agregadas exclusiones para .hypothesis/ y archivos temporales
- `app/database.py` - Configuración de timeouts y pool
- `app/models/product.py` - Campo stock agregado
- `app/routes/products.py` - Soporte para campo stock

### 🎯 Mejoras

- Proyecto más organizado y fácil de navegar
- Documentación consolidada en menos archivos
- Scripts de utilidad en carpeta dedicada
- Mejor manejo de conexiones a base de datos
- Estructura más profesional y mantenible

## Estructura Final

```
Backend-FastApi-EC2/
├── app/              # Código de aplicación
├── tests/            # Tests unitarios
├── scripts/          # Scripts de utilidad
├── docs/             # Documentación extensa
├── README.md         # Documentación principal
├── QUICK_REFERENCE.md # Referencia rápida
└── [archivos de configuración]
```

## Próximos Pasos Recomendados

1. ✅ Commit y push de cambios
2. ✅ Actualizar instancia EC2 con `git pull`
3. ✅ Ejecutar migración: `psql "$DATABASE_URL" -f migrate_database.sql`
4. ✅ Reiniciar servicio: `sudo systemctl restart fastapi`
5. ✅ Crear nueva AMI (v2) con los cambios
6. ✅ Actualizar Auto Scaling Group si aplica
