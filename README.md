# FastAPI + Gunicorn en EC2

API REST básica construida con FastAPI y Gunicorn, diseñada para desplegarse en instancias EC2 de AWS. La aplicación gestiona un inventario simple de productos con operaciones CRUD en memoria.

## Características

- ✅ API REST con FastAPI
- ✅ Validación de datos con Pydantic
- ✅ Servidor de producción con Gunicorn
- ✅ Documentación automática con OpenAPI/Swagger
- ✅ Almacenamiento en memoria
- ✅ Tests unitarios y property-based testing
- ✅ Listo para despliegue en EC2

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

## Instalación Local

### 1. Clonar el Repositorio

```bash
git clone <url-de-tu-repositorio>
cd fastapi-gunicorn-ec2
```

### 2. Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (Opcional)

```bash
cp .env.example .env
# Editar .env según tus necesidades
```

## Ejecución Local

### Modo Desarrollo (con recarga automática)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Producción (con Gunicorn)

```bash
# Usando el script de inicio
chmod +x start.sh
./start.sh

# O directamente con Gunicorn
gunicorn -c gunicorn_config.py app.main:app
```

La aplicación estará disponible en:

- **API**: http://localhost:8000
- **Documentación interactiva**: http://localhost:8000/docs
- **Documentación alternativa**: http://localhost:8000/redoc

## Uso de la API

### Mensaje de Bienvenida

```bash
curl http://localhost:8000/
```

### Crear un Producto

```bash
curl -X POST http://localhost:8000/productos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop",
    "precio": 999.99,
    "descripcion": "Laptop de alta gama"
  }'
```

### Listar Productos

```bash
curl http://localhost:8000/productos
```

## Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar tests específicos
pytest tests/test_models.py
pytest tests/test_routes.py
pytest tests/test_storage.py
```

## Estructura del Proyecto

```
fastapi-gunicorn-ec2/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py       # Modelo de Producto
│   ├── routes/
│   │   ├── __init__.py
│   │   └── products.py      # Endpoints de productos
│   └── storage/
│       ├── __init__.py
│       └── memory.py        # Almacenamiento en memoria
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # Tests del modelo
│   ├── test_routes.py       # Tests de endpoints
│   └── test_storage.py      # Tests de almacenamiento
├── gunicorn_config.py       # Configuración de Gunicorn
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore              # Archivos ignorados por Git
├── README.md               # Este archivo
└── start.sh                # Script de inicio
```

## Despliegue en EC2

### Paso 1: Preparar la Instancia EC2

1. **Lanzar una instancia EC2**

   - AMI: Amazon Linux 2023, Amazon Linux 2, o Ubuntu Server
   - Tipo de instancia: t2.micro (o superior según necesidades)
   - Configurar Security Group (ver Paso 2)

2. **Conectar a la instancia**

```bash
# Para Amazon Linux
ssh -i tu-clave.pem ec2-user@tu-ip-ec2

# Para Ubuntu
ssh -i tu-clave.pem ubuntu@tu-ip-ec2
```

### Paso 2: Configurar Security Group

Debes configurar las reglas de entrada en el Security Group de tu instancia EC2:

**Opción A: Usando la Consola de AWS**

1. Ve a EC2 → Security Groups
2. Selecciona el Security Group de tu instancia
3. Edita las reglas de entrada (Inbound rules)
4. Agrega las siguientes reglas:

| Tipo | Protocolo | Puerto | Origen    | Descripción |
| ---- | --------- | ------ | --------- | ----------- |
| HTTP | TCP       | 8000   | 0.0.0.0/0 | API FastAPI |
| SSH  | TCP       | 22     | Tu IP     | Acceso SSH  |

**Opción B: Usando AWS CLI**

```bash
# Obtener el ID del Security Group
SECURITY_GROUP_ID=$(aws ec2 describe-instances \
  --instance-ids tu-instance-id \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text)

# Agregar regla para puerto 8000
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Verificar las reglas
aws ec2 describe-security-groups \
  --group-ids $SECURITY_GROUP_ID
```

### Paso 3: Instalar Dependencias en EC2

**Para Amazon Linux 2023 / Amazon Linux 2:**

```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

**Para Ubuntu Server:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

### Paso 4: Clonar y Configurar el Proyecto

```bash
# Clonar el repositorio
git clone <url-de-tu-repositorio>
cd fastapi-gunicorn-ec2

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Configurar Variables de Entorno (Opcional)

```bash
cp .env.example .env
nano .env  # Editar según necesidades
```

### Paso 6: Ejecutar la Aplicación

**Opción A: Ejecución Manual**

```bash
chmod +x start.sh
./start.sh
```

**Opción B: Configurar como Servicio Systemd (Recomendado)**

1. Crear archivo de servicio:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

2. Agregar el siguiente contenido (ajusta el usuario según tu distribución):

**Para Amazon Linux:**

```ini
[Unit]
Description=FastAPI Application
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

**Para Ubuntu:**

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/fastapi-gunicorn-ec2
Environment="PATH=/home/ubuntu/fastapi-gunicorn-ec2/venv/bin"
ExecStart=/home/ubuntu/fastapi-gunicorn-ec2/venv/bin/gunicorn -c gunicorn_config.py app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Habilitar e iniciar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

4. Comandos útiles del servicio:

```bash
# Ver logs
sudo journalctl -u fastapi -f

# Reiniciar servicio
sudo systemctl restart fastapi

# Detener servicio
sudo systemctl stop fastapi
```

### Paso 7: Verificar el Despliegue

```bash
# Desde la instancia EC2
curl http://localhost:8000/

# Desde tu máquina local
curl http://tu-ip-ec2:8000/
```

Accede a la documentación en: `http://tu-ip-ec2:8000/docs`

## Configuración de Gunicorn

El archivo `gunicorn_config.py` contiene la configuración de producción:

```python
bind = "0.0.0.0:8000"        # Escucha en todas las interfaces
workers = 4                   # Número de workers
worker_class = "uvicorn.workers.UvicornWorker"  # Worker ASGI
timeout = 120                 # Timeout de 120 segundos
```

Puedes ajustar estos valores según las necesidades de tu instancia EC2.

## Solución de Problemas

### La aplicación no inicia

```bash
# Verificar que el puerto 8000 no esté en uso
sudo lsof -i :8000

# Verificar logs de Gunicorn
sudo journalctl -u fastapi -n 50
```

### No puedo acceder desde el navegador

- Verifica que el Security Group permita tráfico en el puerto 8000
- Verifica que la aplicación esté escuchando en 0.0.0.0 (no en 127.0.0.1)
- Usa la IP pública de EC2, no la privada

### Errores de permisos

```bash
# Asegurar permisos correctos
chmod +x start.sh
chmod -R 755 /home/ec2-user/fastapi-gunicorn-ec2
```

## Mejoras Futuras

- [ ] Agregar base de datos persistente (PostgreSQL, MySQL)
- [ ] Implementar autenticación y autorización
- [ ] Agregar más endpoints CRUD (UPDATE, DELETE)
- [ ] Configurar HTTPS con certificado SSL
- [ ] Implementar rate limiting
- [ ] Agregar monitoreo con CloudWatch
- [ ] Configurar CI/CD con GitHub Actions
- [ ] Dockerizar la aplicación

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

Si encuentras algún problema o tienes preguntas, por favor abre un issue en el repositorio.
