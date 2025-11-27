#!/usr/bin/env python3
"""
Script simple para verificar configuración.
"""

from pathlib import Path

print("🔍 Verificando configuración...")
print()

# 1. Verificar .env
env_path = Path('.env')
if env_path.exists():
    print("✅ .env encontrado")
else:
    print("⚠️  .env NO encontrado - copia .env.example a .env")
    exit(1)

# 2. Cargar config
try:
    from app.config import DATABASE_URL, APP_PORT
    print("✅ Configuración cargada")
    print(f"   Puerto: {APP_PORT}")
    print(f"   Database: {DATABASE_URL[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 3. Probar conexión
try:
    from app.database import engine
    with engine.connect():
        print("✅ Conexión a PostgreSQL OK")
except Exception as e:
    print(f"❌ No se puede conectar a PostgreSQL: {e}")
    exit(1)

print()
print("✅ Todo listo!")
print("Inicia con: ./start.sh")
