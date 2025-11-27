# Guía de Monitoreo y Troubleshooting en EC2

## 📊 Comandos para Monitorear el Despliegue

### 1. Ver logs en tiempo real

```bash
# Ver logs del servicio (recomendado)
sudo journalctl -u fastapi -f

# Ver últimos 50 logs
sudo journalctl -u fastapi -n 50 --no-pager

# Ver logs con timestamps
sudo journalctl -u fastapi -f --since "5 minutes ago"
```

### 2. Ver estado del servicio

```bash
# Estado actual
sudo systemctl status fastapi

# Ver si está activo
sudo systemctl is-active fastapi

# Ver si está habilitado
sudo systemctl is-enabled fastapi
```

### 3. Verificar configuración

```bash
# Ver contenido del .env (sin mostrar passwords completos)
cat .env | sed 's/:.*@/:****@/'

# Verificar que .env existe
ls -la .env

# Probar carga de configuración
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python check_config.py
```

### 4. Verificar conectividad

```bash
# Verificar que el puerto 8000 está escuchando
sudo ss -tlnp | grep 8000

# Probar health check
curl http://localhost:8000/health

# Probar desde fuera (reemplaza con tu IP)
curl http://tu-ip-ec2:8000/health
```

---

## 🔴 Error: "Could not parse SQLAlchemy URL"

### Causa

El DATABASE_URL en `.env` está mal formado o vacío.

### Solución

```bash
# 1. Ver el .env actual
cat .env

# 2. Si está mal, recrearlo
echo "DATABASE_URL=postgresql://usuario:password@host:5432/database" > .env
echo "APP_PORT=8000" >> .env

# 3. Verificar que quedó bien
cat .env

# 4. Reiniciar servicio
sudo systemctl restart fastapi

# 5. Ver logs
sudo journalctl -u fastapi -f
```

### Formato Correcto del DATABASE_URL

```bash
# Formato básico
DATABASE_URL=postgresql://usuario:password@host:5432/database

# Ejemplo real
DATABASE_URL=postgresql://admin:MiPassword123@mi-rds.us-east-1.rds.amazonaws.com:5432/postgres
```

---

## 🔒 Error: RDS Requiere SSL

### Síntoma

```
SSL connection is required
```

### Solución: Agregar parámetros SSL al DATABASE_URL

```bash
# Opción 1: SSL con verificación (recomendado)
DATABASE_URL=postgresql://usuario:password@host:5432/database?sslmode=require

# Opción 2: SSL sin verificar certificado (para desarrollo)
DATABASE_URL=postgresql://usuario:password@host:5432/database?sslmode=require&sslrootcert=/dev/null

# Opción 3: SSL preferido (intenta SSL, si falla usa sin SSL)
DATABASE_URL=postgresql://usuario:password@host:5432/database?sslmode=prefer
```

### Ejemplo Completo con SSL

```bash
# Detener servicio
sudo systemctl stop fastapi

# Actualizar .env con SSL
cat > .env << 'EOF'
DATABASE_URL=postgresql://admin:MiPassword123@mi-rds.us-east-1.rds.amazonaws.com:5432/postgres?sslmode=require
APP_PORT=8000
EOF

# Verificar
cat .env

# Probar conexión manualmente
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python check_config.py

# Si funciona, iniciar servicio
sudo systemctl start fastapi
sudo systemctl status fastapi
```

---

## 🔍 Diagnóstico Paso a Paso

### Paso 1: Verificar que el .env existe y tiene contenido

```bash
cd /home/ec2-user/Backend-FastApi-EC2
ls -la .env
cat .env
```

**Debe mostrar:**

```
DATABASE_URL=postgresql://...
APP_PORT=8000
```

### Paso 2: Probar carga de configuración

```bash
source venv/bin/activate
python3 << 'EOF'
from app.config import DATABASE_URL
print(f"DATABASE_URL cargado: {DATABASE_URL[:50]}...")
EOF
```

**Debe mostrar:**

```
DATABASE_URL cargado: postgresql://admin:****@mi-rds...
```

### Paso 3: Probar conexión a PostgreSQL

```bash
# Instalar psql si no está
sudo yum install postgresql15 -y

# Probar conexión (sin SSL)
psql "postgresql://admin:password@host:5432/postgres"

# Probar conexión (con SSL)
psql "postgresql://admin:password@host:5432/postgres?sslmode=require"
```

### Paso 4: Probar la app manualmente

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate

# Probar con uvicorn directamente
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Si funciona, el problema está en el servicio systemd.

### Paso 5: Verificar permisos

```bash
# Ver permisos del .env
ls -la .env

# Debe ser propiedad de ec2-user
# Si no, arreglar:
sudo chown ec2-user:ec2-user .env
chmod 644 .env
```

---

## 🚀 Script de Diagnóstico Rápido

Crea y ejecuta este script:

```bash
cat > diagnose.sh << 'SCRIPT'
#!/bin/bash
echo "🔍 Diagnóstico de FastAPI en EC2"
echo "================================"
echo ""

cd /home/ec2-user/Backend-FastApi-EC2

echo "1. ¿Existe .env?"
if [ -f .env ]; then
    echo "   ✅ Sí"
    echo "   Contenido (sin passwords):"
    cat .env | sed 's/:.*@/:****@/' | sed 's/^/   /'
else
    echo "   ❌ NO - Este es el problema!"
    exit 1
fi
echo ""

echo "2. ¿Se puede cargar la configuración?"
source venv/bin/activate
python3 << 'EOF'
try:
    from app.config import DATABASE_URL
    print("   ✅ Configuración cargada")
    print(f"   DATABASE_URL: {DATABASE_URL[:60]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)
EOF
echo ""

echo "3. ¿Se puede conectar a PostgreSQL?"
python3 << 'EOF'
try:
    from app.database import engine
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("   ✅ Conexión exitosa")
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    print("   💡 Intenta agregar ?sslmode=require al DATABASE_URL")
    exit(1)
EOF
echo ""

echo "4. Estado del servicio:"
sudo systemctl is-active fastapi
echo ""

echo "5. ¿Puerto 8000 escuchando?"
if sudo ss -tlnp | grep -q 8000; then
    echo "   ✅ Sí"
else
    echo "   ❌ No"
fi
echo ""

echo "✅ Diagnóstico completado"
SCRIPT

chmod +x diagnose.sh
./diagnose.sh
```

---

## 💡 Solución Rápida para tu Caso

Basado en tu error, ejecuta esto:

```bash
# 1. Detener servicio
sudo systemctl stop fastapi

# 2. Ir al directorio
cd /home/ec2-user/Backend-FastApi-EC2

# 3. Crear .env correcto CON SSL
echo "DATABASE_URL=postgresql://TU_USUARIO:TU_PASSWORD@TU_HOST:5432/TU_DATABASE?sslmode=require" > .env
echo "APP_PORT=8000" >> .env

# 4. Verificar
cat .env

# 5. Probar configuración
source venv/bin/activate
python check_config.py

# 6. Si el check pasa, iniciar servicio
sudo systemctl start fastapi

# 7. Ver logs
sudo journalctl -u fastapi -f
```

---

## 📝 Formato DATABASE_URL con SSL

### Para RDS de AWS (requiere SSL):

```bash
# Formato completo
DATABASE_URL=postgresql://USUARIO:PASSWORD@ENDPOINT:5432/DATABASE?sslmode=require

# Ejemplo real
DATABASE_URL=postgresql://admin:MySecurePass123@mydb.abc123.us-east-1.rds.amazonaws.com:5432/postgres?sslmode=require
```

### Opciones de sslmode:

- `disable`: Sin SSL (no funciona con RDS)
- `prefer`: Intenta SSL, si falla usa sin SSL
- `require`: Requiere SSL (recomendado para RDS)
- `verify-ca`: Requiere SSL y verifica certificado
- `verify-full`: Requiere SSL y verifica certificado y hostname

---

## 🎯 Checklist de Verificación

- [ ] .env existe en `/home/ec2-user/Backend-FastApi-EC2/.env`
- [ ] DATABASE_URL tiene formato correcto
- [ ] DATABASE_URL incluye `?sslmode=require` si RDS lo requiere
- [ ] `python check_config.py` pasa sin errores
- [ ] Security Group de RDS permite puerto 5432 desde EC2
- [ ] Security Group de EC2 permite puerto 8000
- [ ] Servicio systemd está habilitado: `sudo systemctl is-enabled fastapi`
- [ ] Logs no muestran errores: `sudo journalctl -u fastapi -n 20`

---

## 🆘 Si Nada Funciona

```bash
# 1. Ver logs completos
sudo journalctl -u fastapi -n 200 --no-pager > /tmp/fastapi-logs.txt
cat /tmp/fastapi-logs.txt

# 2. Probar manualmente
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Si funciona manualmente pero no como servicio:
sudo systemctl edit fastapi
# Agregar:
# [Service]
# Environment="DATABASE_URL=postgresql://..."

# 4. Reiniciar
sudo systemctl daemon-reload
sudo systemctl restart fastapi
```
