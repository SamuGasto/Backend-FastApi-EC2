# Guía de Auto Scaling en AWS

Configuración de Application Load Balancer y Auto Scaling Group para alta disponibilidad.

## Arquitectura

```
Internet → ALB → Target Group → Auto Scaling Group (2-10 EC2) → RDS
```

## Pasos Principales

### 1. Crear AMI

1. EC2 Console → Instances → Selecciona tu instancia
2. Actions → Image and templates → Create image
3. Configuración:
   - Name: `productos-api-v1`
   - No reboot: ✅

### 2. Crear Target Group

1. EC2 Console → Target Groups → Create
2. Configuración:
   - Target type: Instances
   - Name: `productos-api-tg`
   - Protocol: HTTP, Port: 8000
   - Health check path: `/health`
   - Healthy threshold: 2
   - Unhealthy threshold: 3
   - Timeout: 5s
   - Interval: 30s

### 3. Crear Application Load Balancer

1. EC2 Console → Load Balancers → Create
2. Tipo: Application Load Balancer
3. Configuración:
   - Name: `productos-api-alb`
   - Scheme: Internet-facing
   - Subnets: Selecciona 2+ AZs
   - Security Group: Permitir HTTP (80) desde 0.0.0.0/0
   - Listener: HTTP:80 → Forward to `productos-api-tg`

### 4. Crear Launch Template

1. EC2 Console → Launch Templates → Create
2. Configuración:
   - Name: `productos-api-lt`
   - AMI: `productos-api-v1`
   - Instance type: t3.small
   - Key pair: Tu key pair
   - Security Group: El de tu EC2
   - User data:
   ```bash
   #!/bin/bash
   systemctl start fastapi
   systemctl enable fastapi
   ```

### 5. Crear Auto Scaling Group

1. EC2 Console → Auto Scaling Groups → Create
2. Configuración:
   - Name: `productos-api-asg`
   - Launch template: `productos-api-lt`
   - VPC: Tu VPC
   - Subnets: 2-3 subnets privadas
   - Load balancing: Attach to `productos-api-tg`
   - Health checks: ELB + EC2
   - Group size:
     - Desired: 2
     - Minimum: 2
     - Maximum: 10
   - Scaling policy: Target tracking
     - Metric: Average CPU utilization
     - Target: 70%

## Verificación

```bash
# Obtener DNS del ALB
ALB_DNS="productos-api-alb-XXX.elb.amazonaws.com"

# Probar
curl http://$ALB_DNS/health
curl http://$ALB_DNS/productos
```

## Actualizar Deployment

### Crear nueva AMI

1. Actualiza código en EC2 actual
2. Crea nueva AMI (v2, v3, etc.)
3. Actualiza Launch Template con nueva AMI
4. Instance Refresh del ASG:

```bash
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name productos-api-asg \
  --preferences MinHealthyPercentage=50
```

## Security Groups

### ALB Security Group

- Inbound: HTTP (80) desde 0.0.0.0/0
- Outbound: HTTP (8000) a EC2 SG

### EC2 Security Group

- Inbound: HTTP (8000) desde ALB SG
- Outbound: PostgreSQL (5432) a RDS SG

### RDS Security Group

- Inbound: PostgreSQL (5432) desde EC2 SG

## Costos Estimados (us-east-1)

- ALB: ~$16/mes base
- EC2 t3.small: ~$15/mes por instancia
- Total (2 instancias): ~$50-60/mes

## Monitoreo

CloudWatch métricas importantes:

- Target Response Time
- Healthy/Unhealthy Host Count
- Request Count
- CPU Utilization

## Troubleshooting

### Targets no están healthy

```bash
# Verificar en la instancia
curl http://localhost:8000/health

# Ver logs
sudo journalctl -u fastapi -n 50
```

### Auto Scaling no funciona

- Verificar CloudWatch métricas
- Revisar scaling policies
- Verificar health check grace period (300s)
