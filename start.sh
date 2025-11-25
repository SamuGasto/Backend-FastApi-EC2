#!/bin/bash
# Start script for FastAPI application with Gunicorn

gunicorn -c gunicorn_config.py app.main:app
