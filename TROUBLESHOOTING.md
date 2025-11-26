# Troubleshooting Guide

Soluciones a problemas comunes.

## 🔴 Error: "connection to server at localhost (127.0.0.1), port 5432 failed"

### Síntoma

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

### Causa

La aplicación no está leyendo el archivo `.env` correctamente, por lo que usa el valor por defecto (`localhost`).

### Solución

**1. Verificar que el .env existe y tiene el DATABASE_URL correcto:**

```bash
cat /home/ec2-user/Backend-FastApi-EC2/.env
```

Debe mostrar algo como:

```
DATABASE_URL=postgresql://admin:password@tu-rds.rds.amazonaws.com:5432/productos
```

**2. Verificar que python-dotenv está instalado:**

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
pip list | grep python-dotenv
```

Si no aparece, instálalo:

```bash
pip install python-dotenv
```

**3. Hacer commit y push de los cambios:**

```bash
git add app/database.py requirements.txt
git commit -m "Fix: Load .env file with python-dotenv"
git push
```

**4. En tu EC2, actualizar el código:**

```bash
cd /home/ec2-user/Backend-FastApi-EC2
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fastapi
```

**5. Verificar que funciona:**

```bash
sudo systemctl status fastapi
curl http://localhost:8000/health
```

### Verificación Adicional

Si sigue fallando, verifica manualmente que Python puede leer el .env:

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python3 << EOF
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path('.env')
print(f"¿Existe .env? {env_path.exists()}")
print(f"Ruta completa: {env_path.absolute()}")

load_dotenv(dotenv_path=env_path)
db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {db_url[:50]}..." if db_url else "DATABASE_URL: NO ENCONTRADO")
EOF
```

---

## 🔴 Error: "Worker failed to boot"

### Síntoma

```
[ERROR] Worker (pid:5375) exited with code 3
[ERROR] Shutting down: Master
[ERROR] Reason: Worker failed to boot
```

### Causas Comunes

1. Error en el código Python (sintaxis, imports)
2. Dependencias faltantes
3. Permisos incorrectos
4. .env no se puede leer

### Solución

**1. Ver logs detallados:**

```bash
sudo journalctl -u fastapi -n 100 --no-pager
```

**2. Probar manualmente:**

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python3 -c "from app.main import app; print('OK')"
```

Si falla, verás el error exacto.

**3. Probar Gunicorn manualmente:**

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**4. Verificar permisos:**

```bash
ls -la /home/ec2-user/Backend-FastApi-EC2/
# Todo debe ser propiedad de ec2-user:ec2-user
```

Si no:

```bash
sudo chown -R ec2-user:ec2-user /home/ec2-user/Backend-FastApi-EC2
```

---

## 🔴 Error: "No module named 'app'"

### Síntoma

```
ModuleNotFoundError: No module named 'app'
```

### Causa

El `PYTHONPATH` no está configurado correctamente o falta `__init__.py`.

### Solución

**1. Verificar estructura:**

```bash
ls -la /home/ec2-user/Backend-FastApi-EC2/app/
```

Debe tener `__init__.py`.

**2. Verificar que el servicio tiene el WorkingDirectory correcto:**

```bash
cat /etc/systemd/system/fastapi.service | grep WorkingDirectory
```

Debe ser: `WorkingDirectory=/home/ec2-user/Backend-FastApi-EC2`

**3. Reiniciar servicio:**

```bash
sudo systemctl daemon-reload
sudo systemctl restart fastapi
```

---

## 🔴 Error: "Permission denied" al leer .env

### Síntoma

```
PermissionError: [Errno 13] Permission denied: '/home/ec2-user/Backend-FastApi-EC2/.env'
```

### Solución

```bash
cd /home/ec2-user/Backend-FastApi-EC2
chmod 644 .env
chown ec2-user:ec2-user .env
sudo systemctl restart fastapi
```

---

## 🔴 Error: Parameter Store no retorna valor

### Síntoma

El User Data no obtiene el DATABASE_URL de Parameter Store.

### Solución

**1. Verificar que el parámetro existe:**

```bash
aws ssm get-parameter \
  --name "/productos-api/database-url" \
  --with-decryption \
  --region us-east-1
```

**2. Verificar IAM Role de la instancia:**

```bash
# Ver si tiene rol
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Debe mostrar el nombre del rol
```

**3. Verificar permisos del rol:**

El rol debe tener esta policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParameter", "ssm:GetParameters"],
      "Resource": "arn:aws:ssm:us-east-1:*:parameter/productos-api/*"
    },
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "*"
    }
  ]
}
```

**4. Verificar conectividad:**

La instancia necesita acceso a Internet para llamar a la API de SSM:

- Internet Gateway (si está en subnet pública)
- NAT Gateway (si está en subnet privada)

---

## 🔴 Error: "Can't connect to RDS"

### Síntoma

```
psycopg2.OperationalError: could not connect to server
```

### Solución

**1. Verificar Security Group de RDS:**

Debe permitir entrada en puerto 5432 desde:

- Security Group de EC2, O
- CIDR de la VPC

**2. Verificar que RDS está en la misma VPC:**

```bash
# Ver VPC de la instancia
aws ec2 describe-instances \
  --instance-ids $(ec2-metadata --instance-id | cut -d " " -f 2) \
  --query 'Reservations[0].Instances[0].VpcId'

# Ver VPC de RDS
aws rds describe-db-instances \
  --db-instance-identifier tu-db-name \
  --query 'DBInstances[0].DBSubnetGroup.VpcId'
```

**3. Probar conexión manualmente:**

```bash
# Instalar psql
sudo yum install postgresql15 -y

# Probar conexión
psql -h tu-rds-endpoint.rds.amazonaws.com -U admin -d postgres
```

**4. Verificar DNS:**

```bash
nslookup tu-rds-endpoint.rds.amazonaws.com
```

---

## 🔴 Health Check falla en ALB

### Síntoma

Las instancias aparecen como "unhealthy" en el Target Group.

### Solución

**1. Verificar que el endpoint /health responde:**

```bash
curl http://localhost:8000/health
```

**2. Verificar configuración del Target Group:**

- Health check path: `/health`
- Health check port: `8000`
- Success codes: `200`

**3. Verificar Security Group:**

El Security Group de EC2 debe permitir entrada en puerto 8000 desde el Security Group del ALB.

**4. Ver logs:**

```bash
sudo journalctl -u fastapi -f
```

---

## 🔴 Instancias no escalan en ASG

### Síntoma

El ASG no lanza nuevas instancias cuando hay carga.

### Solución

**1. Verificar scaling policies:**

```bash
aws autoscaling describe-policies \
  --auto-scaling-group-name tu-asg-name
```

**2. Verificar métricas de CloudWatch:**

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=tu-asg-name \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average
```

**3. Verificar límites de servicio:**

```bash
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-1216C47A
```

---

## 📊 Comandos Útiles de Debug

### Ver logs en tiempo real

```bash
sudo journalctl -u fastapi -f
```

### Ver últimos 100 logs

```bash
sudo journalctl -u fastapi -n 100 --no-pager
```

### Ver logs de User Data

```bash
sudo cat /var/log/user-data.log
```

### Ver logs de cloud-init

```bash
sudo cat /var/log/cloud-init-output.log
```

### Probar la app manualmente

```bash
cd /home/ec2-user/Backend-FastApi-EC2
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Ver variables de entorno del servicio

```bash
sudo systemctl show fastapi --property=Environment
```

### Ver procesos de Python

```bash
ps aux | grep python
```

### Ver conexiones de red

```bash
sudo netstat -tlnp | grep 8000
```

### Test de conectividad a RDS

```bash
telnet tu-rds-endpoint.rds.amazonaws.com 5432
```

---

## 🆘 Último Recurso

Si nada funciona, reinicia desde cero:

```bash
# Detener servicio
sudo systemctl stop fastapi
sudo systemctl disable fastapi

# Eliminar todo
sudo rm -rf /home/ec2-user/Backend-FastApi-EC2
sudo rm /etc/systemd/system/fastapi.service

# Volver a ejecutar User Data manualmente
sudo bash /var/lib/cloud/instance/user-data.txt
```

---

¿Necesitas más ayuda? Abre un issue en GitHub con:

1. Logs completos: `sudo journalctl -u fastapi -n 200 --no-pager`
2. Contenido de .env (sin passwords): `cat .env | sed 's/:.*/:*****/'`
3. Versión de Python: `python3 --version`
4. Región de AWS: `ec2-metadata --availability-zone`
