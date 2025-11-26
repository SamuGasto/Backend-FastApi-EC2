# Guía Rápida de Setup en EC2

Instrucciones paso a paso para configurar la API en una instancia EC2.

## 📋 Pre-requisitos

- Instancia EC2 (Amazon Linux 2 o Ubuntu)
- Security Group con puerto 8000 abierto
- RDS PostgreSQL configurado
- Acceso SSH a la instancia

## 🚀 Setup Completo

### 1. Conectar a EC2

```bash
ssh -i tu-clave.pem ec2-user@tu-ip-ec2
```

### 2. Instalar dependencias del sistema

**Amazon Linux 2:**

```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

**Ubuntu:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

### 3. Clonar el repositorio

```bash
cd ~
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd fastapi-gunicorn-ec2
```

### 4. Ejecutar setup automático

```bash
chmod +x setup.sh
./setup.sh
```

Esto instalará:

- Entorno virtual Python
- Todas las dependencias
- Creará el archivo .env (vacío)

### 5. Configurar variables de entorno

```bash
nano .env
```

Agrega tu DATABASE_URL:

```bash
DATABASE_URL=postgresql://usuario:password@tu-rds-endpoint:5432/nombre_db
APP_HOST=0.0.0.0
APP_PORT=8000
WORKERS=4
LOG_LEVEL=info
```

**Ejemplo real:**

```bash
DATABASE_URL=postgresql://admin:MiPassword123@productos-db.abc123.us-east-1.rds.amazonaws.com:5432/productos
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

### 6. Probar la aplicación manualmente

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar la app
./start.sh
```

Deberías ver:

```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 1234
```

### 7. Probar desde otra terminal

```bash
# En tu máquina local
curl http://tu-ip-ec2:8000/
curl http://tu-ip-ec2:8000/health
```

Deberías ver:

```json
{ "message": "Bienvenido a la API de Productos" }
```

### 8. Detener la app manual

Presiona `Ctrl+C` en la terminal donde corre la app.

### 9. Configurar como servicio systemd

```bash
# Copiar archivo de servicio
sudo cp fastapi.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable fastapi

# Iniciar servicio
sudo systemctl start fastapi

# Verificar estado
sudo systemctl status fastapi
```

Deberías ver:

```
● fastapi.service - FastAPI Products API
   Loaded: loaded (/etc/systemd/system/fastapi.service; enabled)
   Active: active (running) since ...
```

### 10. Verificar que funciona

```bash
# Desde la instancia EC2
curl http://localhost:8000/health

# Desde tu máquina local
curl http://tu-ip-ec2:8000/health
```

## 🔧 Comandos Útiles

### Ver logs en tiempo real

```bash
sudo journalctl -u fastapi -f
```

### Reiniciar servicio

```bash
sudo systemctl restart fastapi
```

### Detener servicio

```bash
sudo systemctl stop fastapi
```

### Ver estado del servicio

```bash
sudo systemctl status fastapi
```

### Deshabilitar inicio automático

```bash
sudo systemctl disable fastapi
```

## 🐛 Troubleshooting

### El servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u fastapi -n 50 --no-pager

# Verificar que el .env existe
cat /home/ec2-user/fastapi-gunicorn-ec2/.env

# Probar manualmente
cd /home/ec2-user/fastapi-gunicorn-ec2
source venv/bin/activate
./start.sh
```

### No puedo conectarme desde fuera

```bash
# Verificar que el servicio está escuchando
sudo netstat -tlnp | grep 8000

# Verificar Security Group en AWS Console
# Debe permitir puerto 8000 desde tu IP o 0.0.0.0/0
```

### Error de conexión a PostgreSQL

```bash
# Probar conexión manualmente
psql -h tu-rds-endpoint -U admin -d postgres

# Verificar DATABASE_URL en .env
cat .env | grep DATABASE_URL

# Verificar Security Group de RDS
# Debe permitir puerto 5432 desde el Security Group de EC2
```

### Permisos incorrectos

```bash
# Arreglar permisos
cd /home/ec2-user/fastapi-gunicorn-ec2
chmod +x setup.sh start.sh
chown -R ec2-user:ec2-user .
```

## 📊 Verificación Final

Ejecuta estos comandos para verificar que todo está bien:

```bash
# 1. Servicio corriendo
sudo systemctl is-active fastapi
# Debe decir: active

# 2. Servicio habilitado
sudo systemctl is-enabled fastapi
# Debe decir: enabled

# 3. Puerto escuchando
sudo ss -tlnp | grep 8000
# Debe mostrar: LISTEN ... :8000

# 4. Health check
curl http://localhost:8000/health
# Debe retornar: {"status":"healthy",...}

# 5. Crear un producto de prueba
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","precio":99.99}'
# Debe retornar el producto con ID

# 6. Listar productos
curl http://localhost:8000/productos
# Debe retornar array con el producto creado
```

Si todos estos comandos funcionan, ¡tu API está lista! ✅

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

```bash
cd /home/ec2-user/fastapi-gunicorn-ec2

# Obtener últimos cambios
git pull

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias (si cambiaron)
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart fastapi

# Verificar que funciona
curl http://localhost:8000/health
```

## 📚 Próximos Pasos

Una vez que funcione en una instancia:

1. **Crear AMI** de esta instancia
2. **Configurar Auto Scaling Group** con la AMI
3. **Configurar Application Load Balancer**
4. **Configurar API Gateway**

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles.

---

¿Problemas? Revisa los logs: `sudo journalctl -u fastapi -f`
