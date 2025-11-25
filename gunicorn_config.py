# Gunicorn configuration file for FastAPI application

# Server socket
bind = "0.0.0.0:8000"

# Worker processes (ajusta según el tamaño de tu instancia)
# Fórmula: (2 x CPU cores) + 1
workers = 4

# Worker class - use Uvicorn worker for ASGI applications
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout for requests (en segundos)
timeout = 120

# Graceful timeout para shutdown (importante para ASG)
graceful_timeout = 30

# Keep-alive para conexiones persistentes (importante para ALB)
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Preload app para mejor rendimiento
preload_app = True

# Worker restart para evitar memory leaks
max_requests = 1000
max_requests_jitter = 50
