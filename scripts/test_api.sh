#!/bin/bash

# Script de pruebas para la API de Productos
# Uso: bash test_api.sh [URL_BASE]
# Ejemplo: bash test_api.sh http://localhost:8000

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base de la API (por defecto localhost)
BASE_URL="${1:-http://localhost:8000}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Pruebas de API de Productos${NC}"
echo -e "${YELLOW}  URL: $BASE_URL${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Función para imprimir resultados
print_test() {
    echo -e "\n${YELLOW}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Health Check
print_test "1. Health Check"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 2. Endpoint raíz
print_test "2. Endpoint Raíz"
curl -s "$BASE_URL/" | python -m json.tool
echo ""

# 3. Listar productos (inicialmente vacío)
print_test "3. Listar Productos (inicial)"
curl -s "$BASE_URL/productos" | python -m json.tool
echo ""

# 4. Crear primer producto
print_test "4. Crear Producto #1 - Laptop"
PRODUCTO1=$(curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop HP",
    "descripcion": "Laptop HP 15 pulgadas, 8GB RAM, 256GB SSD",
    "precio": 899.99,
    "stock": 10
  }')
echo "$PRODUCTO1" | python -m json.tool
PRODUCTO1_ID=$(echo "$PRODUCTO1" | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo ""

# 5. Crear segundo producto
print_test "5. Crear Producto #2 - Mouse"
PRODUCTO2=$(curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mouse Logitech",
    "descripcion": "Mouse inalámbrico ergonómico",
    "precio": 29.99,
    "stock": 50
  }')
echo "$PRODUCTO2" | python -m json.tool
PRODUCTO2_ID=$(echo "$PRODUCTO2" | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo ""

# 6. Crear tercer producto
print_test "6. Crear Producto #3 - Teclado"
PRODUCTO3=$(curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Teclado Mecánico",
    "descripcion": "Teclado mecánico RGB retroiluminado",
    "precio": 79.99,
    "stock": 25
  }')
echo "$PRODUCTO3" | python -m json.tool
PRODUCTO3_ID=$(echo "$PRODUCTO3" | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo ""

# 7. Listar todos los productos
print_test "7. Listar Todos los Productos"
curl -s "$BASE_URL/productos" | python -m json.tool
echo ""

# 8. Obtener producto específico
if [ ! -z "$PRODUCTO1_ID" ]; then
    print_test "8. Obtener Producto por ID ($PRODUCTO1_ID)"
    curl -s "$BASE_URL/productos/$PRODUCTO1_ID" | python -m json.tool
    echo ""
fi

# 9. Actualizar producto
if [ ! -z "$PRODUCTO2_ID" ]; then
    print_test "9. Actualizar Producto #2 (Mouse) - Cambiar precio y stock"
    curl -s -X PUT "$BASE_URL/productos/$PRODUCTO2_ID" \
      -H "Content-Type: application/json" \
      -d '{
        "nombre": "Mouse Logitech MX Master",
        "descripcion": "Mouse inalámbrico ergonómico premium",
        "precio": 99.99,
        "stock": 30
      }' | python -m json.tool
    echo ""
fi

# 10. Verificar actualización
if [ ! -z "$PRODUCTO2_ID" ]; then
    print_test "10. Verificar Actualización del Producto #2"
    curl -s "$BASE_URL/productos/$PRODUCTO2_ID" | python -m json.tool
    echo ""
fi

# 11. Eliminar producto
if [ ! -z "$PRODUCTO3_ID" ]; then
    print_test "11. Eliminar Producto #3 (Teclado)"
    curl -s -X DELETE "$BASE_URL/productos/$PRODUCTO3_ID" | python -m json.tool
    echo ""
fi

# 12. Verificar eliminación
print_test "12. Listar Productos Después de Eliminación"
curl -s "$BASE_URL/productos" | python -m json.tool
echo ""

# 13. Intentar obtener producto eliminado (debe dar 404)
if [ ! -z "$PRODUCTO3_ID" ]; then
    print_test "13. Intentar Obtener Producto Eliminado (debe fallar)"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/productos/$PRODUCTO3_ID")
    if [ "$HTTP_CODE" == "404" ]; then
        print_success "Producto no encontrado (404) - Correcto"
    else
        print_error "Código HTTP inesperado: $HTTP_CODE"
    fi
    echo ""
fi

# 14. Prueba de validación - Producto con precio negativo
print_test "14. Validación - Intentar Crear Producto con Precio Negativo"
curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto Inválido",
    "descripcion": "Este producto no debería crearse",
    "precio": -10.00,
    "stock": 5
  }' | python -m json.tool
echo ""

# 15. Prueba de validación - Producto con stock negativo
print_test "15. Validación - Intentar Crear Producto con Stock Negativo"
curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto Inválido 2",
    "descripcion": "Este producto tampoco debería crearse",
    "precio": 50.00,
    "stock": -5
  }' | python -m json.tool
echo ""

# Resumen final
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Pruebas Completadas${NC}"
echo -e "${YELLOW}========================================${NC}"
print_test "Estado Final de la Base de Datos"
curl -s "$BASE_URL/productos" | python -m json.tool
echo ""

print_success "Todas las pruebas han sido ejecutadas"
echo -e "\n${YELLOW}Documentación interactiva disponible en:${NC}"
echo -e "  - Swagger UI: $BASE_URL/docs"
echo -e "  - ReDoc: $BASE_URL/redoc\n"
