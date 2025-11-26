# Arquitectura de Producción con API Gateway + ALB + ASG

Guía para desplegar la API con alta disponibilidad y escalabilidad.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (REST API)                    │
│  - Autenticación (API Keys, Cognito, Lambda)                │
│  - Rate limiting                                             │
│  - Caching                                                   │
│  - Logging                                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              VPC Link (opcional, para privado)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           Application Load Balancer (ALB)                    │
│  - Health checks                                             │
│  - SSL/TLS termination                                       │
│  - Sticky sessions (si necesario)                            │
│  - Target Group: EC2 instances                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Auto Scaling Group (ASG)                        │
│  - Min: 2 instancias                                         │
│  - Max: 10 instancias                                        │
│  - Desired: 2 instancias                                     │
│  - Health check: ELB + EC2                                   │
│  - Scaling policies: CPU, requests, custom metrics          │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌────────┐         ┌────────┐         ┌────────┐
   │  EC2   │         │  EC2   │         │  EC2   │
   │ FastAPI│         │ FastAPI│         │ FastAPI│
   └────┬───┘         └────┬───┘         └────┬───┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  RDS PostgreSQL │
                  │  (Multi-AZ)     │
                  └─────────────────┘
```

## 📋 Checklist de Implementación

### 1. Preparar la Aplicación

- [x] Health check endpoint (`/health`)
- [x] Configuración de Gunicorn optimizada
- [x] Logs a stdout/stderr (para CloudWatch)
- [ ] Variables de entorno desde Parameter Store o Secrets Manager
- [ ] Métricas custom (opcional)

### 2. Crear AMI (Amazon Machine Image)

```bash
# En tu EC2 de desarrollo
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clonar y configurar
git clone https://github.com/SamuGasto/Backend-FastApi-EC2.git
cd Backend-FastApi-EC2
chmod +x setup.sh
./setup.sh

# Configurar como servicio systemd
# El archivo fastapi.service ya está en el repositorio
sudo cp fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi

# NO iniciar el servicio aún (se iniciará en las nuevas instancias)
# NO configurar .env aquí (se hará con User Data)

# Crear AMI desde la consola de AWS
# EC2 → Instances → Select instance → Actions → Image and templates → Create image
```

### 3. Configurar Launch Template

**User Data Script** (para configurar .env automáticamente):

```bash
#!/bin/bash
# User Data para Launch Template

# Obtener DATABASE_URL desde Parameter Store
DATABASE_URL=$(aws ssm get-parameter --name "/productos-api/database-url" --with-decryption --query "Parameter.Value" --output text --region us-east-1)

# Crear .env
cat > /home/ec2-user/fastapi-gunicorn-ec2/.env << EOF
DATABASE_URL=$DATABASE_URL
APP_HOST=0.0.0.0
APP_PORT=8000
WORKERS=4
LOG_LEVEL=info
EOF

# Cambiar permisos
chown ec2-user:ec2-user /home/ec2-user/fastapi-gunicorn-ec2/.env

# Iniciar servicio
systemctl start fastapi
systemctl status fastapi
```

**Configuración del Launch Template:**

- AMI: Tu AMI creada
- Instance type: t3.small o t3.medium (según carga)
- Key pair: Tu key pair
- Security group: Permitir puerto 8000 desde ALB
- IAM role: Con permisos para SSM Parameter Store
- User data: Script de arriba

### 4. Configurar Application Load Balancer

**Target Group:**

- Protocol: HTTP
- Port: 8000
- Health check path: `/health`
- Health check interval: 30 segundos
- Healthy threshold: 2
- Unhealthy threshold: 3
- Timeout: 5 segundos
- Success codes: 200

**Load Balancer:**

- Scheme: Internet-facing (o internal si usas VPC Link)
- Listeners:
  - HTTP:80 → Redirect to HTTPS:443
  - HTTPS:443 → Forward to Target Group
- Security group: Permitir 80, 443 desde Internet
- Subnets: Al menos 2 AZs

### 5. Configurar Auto Scaling Group

**Configuración básica:**

```
Min capacity: 2
Max capacity: 10
Desired capacity: 2
Health check type: ELB
Health check grace period: 300 segundos
```

**Scaling Policies:**

**Policy 1: CPU-based scaling**

```
Metric: Average CPU Utilization
Target value: 70%
```

**Policy 2: Request count scaling**

```
Metric: ALBRequestCountPerTarget
Target value: 1000 requests per target
```

**Policy 3: Custom metric (opcional)**

```
Metric: Database connections
Target value: 80% of max connections
```

### 6. Configurar API Gateway

**Opción A: HTTP API (más simple, más barato)**

```bash
# Crear HTTP API
aws apigatewayv2 create-api \
  --name productos-api \
  --protocol-type HTTP \
  --target "http://tu-alb-dns.us-east-1.elb.amazonaws.com"

# Configurar integración
aws apigatewayv2 create-integration \
  --api-id <api-id> \
  --integration-type HTTP_PROXY \
  --integration-uri "http://tu-alb-dns.us-east-1.elb.amazonaws.com" \
  --integration-method ANY \
  --payload-format-version 1.0

# Crear ruta
aws apigatewayv2 create-route \
  --api-id <api-id> \
  --route-key 'ANY /{proxy+}' \
  --target integrations/<integration-id>
```

**Opción B: REST API (más features)**

1. Crear REST API en consola
2. Crear recurso: `{proxy+}`
3. Crear método: `ANY`
4. Integration type: HTTP Proxy
5. Endpoint URL: `http://tu-alb-dns/{proxy}`
6. Deploy to stage: `prod`

**Configurar:**

- Rate limiting (throttling)
- API Keys (si necesitas)
- CORS (si es necesario)
- Custom domain (opcional)

### 7. Configurar RDS

**Recomendaciones:**

- Multi-AZ: Sí (para alta disponibilidad)
- Instance class: db.t3.micro (Free tier) o db.t3.small
- Storage: 20 GB SSD (gp3)
- Backup retention: 7 días
- Encryption: Habilitado
- Security group: Solo desde EC2 security group

**Connection pooling:**

Actualiza `app/database.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Conexiones en el pool
    max_overflow=20,       # Conexiones extra si es necesario
    pool_pre_ping=True,    # Verificar conexión antes de usar
    pool_recycle=3600      # Reciclar conexiones cada hora
)
```

### 8. Configurar CloudWatch

**Logs:**

- Instalar CloudWatch Agent en EC2
- Enviar logs de Gunicorn a CloudWatch
- Crear alarmas para errores

**Métricas importantes:**

- ALB: TargetResponseTime, HTTPCode_Target_5XX_Count
- ASG: GroupDesiredCapacity, GroupInServiceInstances
- RDS: CPUUtilization, DatabaseConnections
- Custom: Request latency, Database query time

**Alarmas sugeridas:**

```
1. ALB 5XX errors > 10 en 5 minutos
2. RDS CPU > 80% por 10 minutos
3. ASG unhealthy instances > 0
4. API Gateway 4XX rate > 20%
```

## 🔒 Security Best Practices

### 1. Network Security

```
┌─────────────────────────────────────────┐
│  Public Subnets (ALB)                   │
│  - 0.0.0.0/0 → 80, 443                  │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Private Subnets (EC2)                  │
│  - ALB SG → 8000                        │
│  - No internet directo                  │
│  - NAT Gateway para updates             │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Private Subnets (RDS)                  │
│  - EC2 SG → 5432                        │
│  - No acceso público                    │
└─────────────────────────────────────────┘
```

### 2. IAM Roles

**EC2 Role:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParameter", "ssm:GetParameters"],
      "Resource": "arn:aws:ssm:*:*:parameter/productos-api/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Secrets Management

**Guardar DATABASE_URL en Parameter Store:**

```bash
aws ssm put-parameter \
  --name "/productos-api/database-url" \
  --value "postgresql://user:pass@endpoint:5432/db" \
  --type "SecureString" \
  --description "Database URL for productos API"
```

## 💰 Estimación de Costos (us-east-1)

**Configuración mínima:**

- API Gateway: ~$3.50/millón de requests
- ALB: ~$16/mes + $0.008/LCU-hour
- EC2 (2x t3.small): ~$30/mes
- RDS (db.t3.micro): Free tier o ~$15/mes
- Data transfer: Variable

**Total estimado: $50-80/mes** (sin Free Tier)

## 🚀 Deployment Workflow

```bash
# 1. Hacer cambios en código
git add .
git commit -m "Update feature"
git push

# 2. Crear nueva AMI
# (Desde consola o con Packer)

# 3. Actualizar Launch Template
aws ec2 create-launch-template-version \
  --launch-template-id lt-xxx \
  --source-version 1 \
  --launch-template-data '{"ImageId":"ami-nueva"}'

# 4. Actualizar ASG (rolling update)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name productos-asg \
  --preferences '{"MinHealthyPercentage":50}'

# 5. Monitorear deployment
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name productos-asg
```

## 📊 Monitoring Dashboard

**CloudWatch Dashboard sugerido:**

- API Gateway: Request count, Latency, 4XX/5XX errors
- ALB: Target response time, Healthy hosts, Request count
- ASG: Desired/Current capacity, CPU utilization
- RDS: Connections, CPU, Storage
- Custom: Database query time, Cache hit rate

## 🔧 Troubleshooting

**Instancias no pasan health check:**

```bash
# SSH a la instancia
ssh -i key.pem ec2-user@ip

# Ver logs
sudo journalctl -u fastapi -f

# Probar health check localmente
curl http://localhost:8000/health

# Ver conexión a RDS
psql -h rds-endpoint -U admin -d postgres
```

**Alta latencia:**

- Verificar RDS connections
- Revisar slow queries
- Aumentar pool_size en database.py
- Considerar caching (Redis/ElastiCache)

**Scaling no funciona:**

- Verificar CloudWatch metrics
- Revisar scaling policies
- Confirmar health check grace period

## 📚 Recursos Adicionales

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)

---

¿Preguntas? Abre un issue en GitHub.
