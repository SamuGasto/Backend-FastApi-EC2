#!/bin/bash
# Script de despliegue automatizado para EC2
# Uso: ./deploy-ec2.sh "postgresql://user:pass@host:5432/db"

set -e  # Exit on error

echo "🚀 Iniciando despliegue en EC2..."
echo ""

# Verificar que se pasó el DATABASE_URL
if [ -z "$1" ]; then
    echo "❌ Error: Debes proporcionar el DATABASE_URL"
    echo ""
    echo "Uso: ./deploy-ec2.sh \"postgresql://user:pass@host:5432/db\""
    echo ""
    echo "Ejemplo:"
    echo "./deploy-ec2.sh \"postgresql://admin:mypass@my-rds.us-east-1.rds.amazonaws.com:5432/postgres\""
    exit 1
fi

DATABASE_URL="$1"

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo yum update -y

# 2. Instalar dependencias
echo "📥 Instalando dependencias..."
sudo yum install python3 python3-pip git -y

# 3. Clonar repositorio (si no existe)
if [ ! -d "Backend-FastApi-EC2" ]; then
    echo "📂 Clonando repositorio..."
    git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
fi

cd Backend-FastApi-EC2

# 4. Setup
echo "⚙️  Ejecutando setup..."
chmod +x setup.sh
./setup.sh

# 5. Configurar .env
echo "📝 Configurando .env..."
cat > .env << EOF
DATABASE_URL=$DATABASE_URL
APP_PORT=8000
EOF

echo "✅ .env creado"

# 6. Verificar configuración
echo "🔍 Verificando configuración..."
source venv/bin/activate
python check_config.py

if [ $? -ne 0 ]; then
    echo "❌ Error en la configuración"
    exit 1
fi

# 7. Copiar servicio systemd
echo "🔧 Configurando servicio systemd..."
sudo cp fastapi.service /etc/systemd/system/

# 8. Iniciar servicio
echo "🚀 Iniciando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# 9. Esperar a que inicie
echo "⏳ Esperando a que el servicio inicie..."
sleep 5

# 10. Verificar estado
echo ""
echo "📊 Estado del servicio:"
sudo systemctl status fastapi --no-pager

# 11. Probar health check
echo ""
echo "🏥 Probando health check..."
sleep 2
curl -f http://localhost:8000/health

if [ $? -eq 0 ]; then
    echo ""
    echo ""
    echo "✅ ¡Despliegue completado exitosamente!"
    echo ""
    echo "📍 Tu API está corriendo en:"
    echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
    echo ""
    echo "📖 Documentación:"
    echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
    echo ""
    echo "💡 Comandos útiles:"
    echo "   Ver logs:      sudo journalctl -u fastapi -f"
    echo "   Reiniciar:     sudo systemctl restart fastapi"
    echo "   Ver estado:    sudo systemctl status fastapi"
else
    echo ""
    echo "❌ Error: El servicio no responde"
    echo "Ver logs: sudo journalctl -u fastapi -n 50"
    exit 1
fi
