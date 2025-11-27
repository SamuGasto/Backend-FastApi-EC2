# API de Productos - FastAPI + PostgreSQL

API REST simple para gestionar productos. Para tests de estrés.

## Setup Rápido

```bash
# 1. Clonar
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd Backend-FastApi-EC2

# 2. Instalar
./setup.sh

# 3. Configurar .env
cp .env.example .env
nano .env  # Pega tu DATABASE_URL

# 4. Verificar
source venv/bin/activate
python check_config.py

# 5. Iniciar
./start.sh
```

Abre: http://localhost:8000/docs

## Endpoints

```bash
# Crear producto
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop", "precio": 999.99}'

# Listar productos
curl http://localhost:8000/productos

# Obtener uno
curl http://localhost:8000/productos/1

# Actualizar
curl -X PUT http://localhost:8000/productos/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Laptop Pro", "precio": 1299.99}'

# Eliminar
curl -X DELETE http://localhost:8000/productos/1

# Health check
curl http://localhost:8000/health
```

## Despliegue en EC2

```bash
# Conectar
ssh -i tu-clave.pem ec2-user@tu-ip-ec2

# Instalar
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clonar
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd Backend-FastApi-EC2

# Setup
./setup.sh

# Configurar .env (reemplaza con tu DATABASE_URL real)
echo "DATABASE_URL=postgresql://admin:password@tu-rds-endpoint:5432/postgres" > .env
echo "APP_PORT=8000" >> .env

# Copiar servicio
sudo cp fastapi.service /etc/systemd/system/

# Iniciar
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# Verificar
sudo systemctl status fastapi
curl http://localhost:8000/health
```

**Abrir puerto 8000 en Security Group!**

### Despliegue Automatizado (Recomendado)

```bash
# Descargar y ejecutar script de despliegue
curl -O https://raw.githubusercontent.com/SamuGasto/Backend-FastApi-EC2/main/deploy-ec2.sh
chmod +x deploy-ec2.sh

# Ejecutar (reemplaza con tu DATABASE_URL real)
./deploy-ec2.sh "postgresql://admin:password@tu-rds-endpoint:5432/postgres"
```

El script hace todo automáticamente:

- ✅ Instala dependencias
- ✅ Clona el repositorio
- ✅ Configura el .env
- ✅ Verifica la configuración
- ✅ Inicia el servicio
- ✅ Prueba que funciona

## Configurar PostgreSQL (RDS)

1. Crear DB en RDS (PostgreSQL, Free tier)
2. Security Group de RDS: permitir puerto 5432 desde EC2
3. Obtener endpoint de RDS
4. Configurar en .env:
   ```
   DATABASE_URL=postgresql://admin:password@tu-rds-endpoint:5432/postgres
   ```

## Tests

```bash
pytest -v
```

## Troubleshooting

```bash
# Ver logs
sudo journalctl -u fastapi -f

# Reiniciar
sudo systemctl restart fastapi

# Probar conexión a DB
psql -h tu-rds-endpoint -U admin -d postgres
```

## Variables de Entorno

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db  # Requerido
APP_PORT=8000                                      # Opcional
```

---

Hecho con ❤️ y FastAPI
