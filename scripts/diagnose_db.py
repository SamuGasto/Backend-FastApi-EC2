#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de conexión a RDS
"""

import os
import sys
import time
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def parse_db_url(url):
    """Parsear DATABASE_URL"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'database': parsed.path.lstrip('/').split('?')[0]
    }

def test_tcp_connection(host, port, timeout=5):
    """Probar conexión TCP al host:port"""
    print(f"\n🔌 Probando conexión TCP a {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.time()
        result = sock.connect_ex((host, port))
        elapsed = time.time() - start
        sock.close()
        
        if result == 0:
            print(f"✅ Conexión TCP exitosa ({elapsed:.2f}s)")
            return True
        else:
            print(f"❌ No se puede conectar al puerto {port}")
            print(f"   Error code: {result}")
            return False
    except socket.gaierror:
        print(f"❌ No se puede resolver el hostname: {host}")
        return False
    except socket.timeout:
        print(f"❌ Timeout después de {timeout}s")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_postgres_connection():
    """Probar conexión a PostgreSQL"""
    print("\n🐘 Probando conexión a PostgreSQL...")
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        db_info = parse_db_url(DATABASE_URL)
        
        # Extraer password del URL
        parsed = urlparse(DATABASE_URL)
        password = parsed.password
        
        start = time.time()
        conn = psycopg2.connect(
            host=db_info['host'],
            port=db_info['port'],
            user=db_info['user'],
            password=password,
            database=db_info['database'],
            connect_timeout=10,
            sslmode='require'
        )
        elapsed = time.time() - start
        
        # Ejecutar query simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Conexión PostgreSQL exitosa ({elapsed:.2f}s)")
        print(f"   Versión: {version[:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Error de conexión PostgreSQL:")
        print(f"   {e}")
        return False
    except ImportError:
        print("⚠️  psycopg2 no instalado, saltando prueba PostgreSQL")
        print("   Instalar con: pip install psycopg2-binary")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_sqlalchemy_connection():
    """Probar conexión con SQLAlchemy"""
    print("\n🔧 Probando conexión con SQLAlchemy...")
    try:
        from sqlalchemy import create_engine, text
        
        start = time.time()
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000"
            }
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        elapsed = time.time() - start
        print(f"✅ Conexión SQLAlchemy exitosa ({elapsed:.2f}s)")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión SQLAlchemy:")
        print(f"   {e}")
        return False

def check_security_groups():
    """Verificar configuración de Security Groups"""
    print("\n🔒 Verificación de Security Groups:")
    print("   Para que funcione, necesitas:")
    print("   1. Security Group de RDS debe permitir:")
    print("      - Inbound: PostgreSQL (5432) desde Security Group de EC2")
    print("   2. Security Group de EC2 debe permitir:")
    print("      - Outbound: All traffic (o al menos PostgreSQL a RDS)")
    print("\n   Verifica en AWS Console:")
    print("   - RDS → Tu instancia → Connectivity & security → Security groups")
    print("   - EC2 → Security Groups → Inbound/Outbound rules")

def main():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL no está configurado en .env")
        sys.exit(1)
    
    # Parsear información
    db_info = parse_db_url(DATABASE_URL)
    print(f"\n📋 Información de conexión:")
    print(f"   Host: {db_info['host']}")
    print(f"   Port: {db_info['port']}")
    print(f"   User: {db_info['user']}")
    print(f"   Database: {db_info['database']}")
    
    # Pruebas
    tcp_ok = test_tcp_connection(db_info['host'], db_info['port'])
    
    if not tcp_ok:
        print("\n" + "=" * 60)
        print("❌ PROBLEMA ENCONTRADO: No hay conectividad TCP")
        print("=" * 60)
        check_security_groups()
        print("\n💡 Solución:")
        print("   1. Ve a AWS Console → RDS → Tu instancia")
        print("   2. Click en el Security Group")
        print("   3. Edit inbound rules")
        print("   4. Add rule:")
        print("      - Type: PostgreSQL")
        print("      - Port: 5432")
        print("      - Source: Security Group de tu EC2")
        sys.exit(1)
    
    pg_ok = test_postgres_connection()
    sa_ok = test_sqlalchemy_connection()
    
    print("\n" + "=" * 60)
    if tcp_ok and (pg_ok or sa_ok):
        print("✅ DIAGNÓSTICO COMPLETO: Todo funciona correctamente")
        print("=" * 60)
        print("\n💡 Si aún tienes problemas con /productos:")
        print("   1. Reinicia el servicio: sudo systemctl restart fastapi")
        print("   2. Verifica logs: sudo journalctl -u fastapi -n 50")
        print("   3. Prueba directamente: curl http://localhost:8000/productos")
    else:
        print("⚠️  DIAGNÓSTICO COMPLETO: Hay problemas de conexión")
        print("=" * 60)
        check_security_groups()
    
    print()

if __name__ == "__main__":
    main()
