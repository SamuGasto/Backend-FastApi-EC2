-- Migración: Agregar campo stock a la tabla products
-- Fecha: 2024-11-27
-- Descripción: Agrega columna stock para control de inventario

-- Agregar columna stock si no existe
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock INTEGER NOT NULL DEFAULT 0;

-- Actualizar productos existentes con stock por defecto
UPDATE products SET stock = 0 WHERE stock IS NULL;

-- Verificar la estructura de la tabla
\d products

-- Verificar datos
SELECT id, nombre, precio, stock FROM products LIMIT 5;
