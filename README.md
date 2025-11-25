# API de Productos - FastAPI + PostgreSQL 🚀

API REST para gestionar productos. Simple, directa, lista para EC2.

## Setup en 3 Pasos

### 1. Clonar e instalar

```bash
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd fastapi-gunicorn-ec2
chmod +x setup.sh
./setup.sh
```

### 2. Configurar base de datos

Edita `.env`:

```bash
nano .env
```

Agrega tu DATABASE_URL:

```
DATABASE_URL=postgresql://usuario:password@tu-endpoint:5432/nombre_db
```

### 3. Iniciar

```bash
source venv/bin/activate
./start.sh
```

✅ Listo! API en `http://localhost:8000/docs`

---

## Despliegue en EC2

```bash
# Conectar
ssh -i tu-clave.pem ec2-user@tu-ip-ec2

# Instalar
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clonar
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd fastapi-gunicorn-ec2

# Setup
chmod +x setup.sh
./setup.sh

# Configurar .env con tu DATABASE_URL
nano .env

# Iniciar
source venv/bin/activate
chmod +x start.sh
./start.sh
```

**No olvides abrir el puerto 8000 en tu Security Group!**

### Hacerlo un servicio

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Pega:

```ini
[Unit]
Description=FastAPI Products API
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/fastapi-gunicorn-ec2
Environment="PATH=/home/ec2-user/fastapi-gunicorn-ec2/venv/bin"
ExecStart=/home/ec2-user/fastapi-gunicorn-ec2/venv/bin/gunicorn -c gunicorn_config.py app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
```

---

## Endpoints

### Crear producto

```bash
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop", "precio": 999.99}'
```

### Listar todos

```bash
curl http://localhost:8000/productos
```

### Obtener uno

```bash
curl http://localhost:8000/productos/1
```

### Actualizar

```bash
curl -X PUT http://localhost:8000/productos/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop Pro", "precio": 1299.99}'
```

### Eliminar

```bash
curl -X DELETE http://localhost:8000/productos/1
```

---

## Configurar PostgreSQL (RDS)

1. **Crear DB en RDS:**

   - Engine: PostgreSQL
   - Template: Free tier
   - Username: admin
   - Password: (elige una)

2. **Security Group de RDS:**

   - Agregar regla: PostgreSQL (5432)
   - Source: Security Group de tu EC2

3. **Obtener endpoint** (en consola RDS)

4. **Configurar .env:**
   ```
   DATABASE_URL=postgresql://admin:tu_password@tu-endpoint:5432/postgres
   ```

---

## Troubleshooting

**No conecta a PostgreSQL:**

- Verifica DATABASE_URL en .env
- Confirma Security Group de RDS permite conexiones desde EC2

**Puerto ocupado:**

- Cambia puerto en `gunicorn_config.py`

**Ver logs:**

```bash
sudo journalctl -u fastapi -f
```

---

## Comandos Útiles

```bash
# Reiniciar
sudo systemctl restart fastapi

# Ver estado
sudo systemctl status fastapi

# Actualizar código
git pull
sudo systemctl restart fastapi
```

---

## 🏗️ Arquitectura de Producción

Para despliegue con **API Gateway + ALB + Auto Scaling**, lee la guía completa:

👉 **[ARCHITECTURE.md](ARCHITECTURE.md)**

Incluye:

- Configuración de ALB y ASG
- Health checks y scaling policies
- API Gateway setup
- Security best practices
- Estimación de costos
- Troubleshooting

---

Documentación interactiva: `/docs`

Hecho con ❤️ y FastAPI
