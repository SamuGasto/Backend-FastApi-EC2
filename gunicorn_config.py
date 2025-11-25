# Gunicorn configuration file for FastAPI application

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 4

# Worker class - use Uvicorn worker for ASGI applications
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout for requests (in seconds)
timeout = 120

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
