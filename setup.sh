#!/bin/bash
# Setup automático para API de Productos con PostgreSQL

echo "🚀 Configurando API de Productos"
echo "================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Configurar .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de PostgreSQL"
    echo "   nano .env"
    echo ""
else
    echo "✅ Archivo .env ya existe"
fi

echo ""
echo "✅ Setup completado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita .env con tu DATABASE_URL:"
echo "   nano .env"
echo ""
echo "2. Activa el entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "3. Inicia la aplicación:"
echo "   ./start.sh"
echo ""
echo "   O en desarrollo:"
echo "   uvicorn app.main:app --reload"
