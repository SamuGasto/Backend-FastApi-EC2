#!/bin/bash
# User Data Script para Launch Template
# Este script se ejecuta automáticamente cuando se lanza una nueva instancia EC2

set -e  # Exit on error

# Logging
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Starting User Data Script ==="
date

# Variables
APP_DIR="/home/ec2-user/fastapi-gunicorn-ec2"
REGION="us-east-1"  # Ajusta según tu región

# 1. Obtener DATABASE_URL desde Parameter Store
echo "Fetching DATABASE_URL from Parameter Store..."
DATABASE_URL=$(aws ssm get-parameter \
  --name "/productos-api/database-url" \
  --with-decryption \
  --query "Parameter.Value" \
  --output text \
  --region $REGION)

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: Failed to fetch DATABASE_URL from Parameter Store"
    exit 1
fi

echo "DATABASE_URL fetched successfully"

# 2. Crear archivo .env
echo "Creating .env file..."
cat > $APP_DIR/.env << EOF
# Database
DATABASE_URL=$DATABASE_URL

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
WORKERS=4
LOG_LEVEL=info

# Environment
ENVIRONMENT=production
EOF

# Cambiar permisos
chown ec2-user:ec2-user $APP_DIR/.env
chmod 600 $APP_DIR/.env

echo ".env file created"

# 3. Activar entorno virtual e instalar dependencias (por si acaso)
echo "Checking dependencies..."
cd $APP_DIR
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 4. Iniciar servicio FastAPI
echo "Starting FastAPI service..."
systemctl daemon-reload
systemctl enable fastapi
systemctl start fastapi

# 5. Esperar a que el servicio esté listo
echo "Waiting for service to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "Service is healthy!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# 6. Verificar estado del servicio
echo "Checking service status..."
systemctl status fastapi --no-pager

# 7. Test health endpoint
echo "Testing health endpoint..."
curl http://localhost:8000/health

echo "=== User Data Script Completed Successfully ==="
date
