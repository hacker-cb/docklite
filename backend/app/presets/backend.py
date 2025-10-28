from . import Preset

# Backend frameworks

NODEJS_EXPRESS = Preset(
    id="nodejs-express",
    name="Node.js + Express",
    description="Node.js приложение с Express фреймворком",
    category="backend",
    icon="💚",
    compose_content="""version: '3.8'

services:
  app:
    image: node:20-alpine
    working_dir: /app
    ports:
      - "${PORT:-3000}:3000"
    volumes:
      - ./app:/app
    command: sh -c "npm install && npm start"
    environment:
      - NODE_ENV=${NODE_ENV:-development}
      - PORT=3000
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "3000",
        "NODE_ENV": "production"
    },
    tags=["nodejs", "express", "javascript"]
)

PYTHON_FASTAPI = Preset(
    id="python-fastapi",
    name="Python + FastAPI",
    description="Python API с FastAPI фреймворком",
    category="backend",
    icon="🐍",
    compose_content="""version: '3.8'

services:
  api:
    image: python:3.11-slim
    working_dir: /app
    ports:
      - "${PORT:-8000}:8000"
    volumes:
      - ./app:/app
    command: sh -c "pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "8000"
    },
    tags=["python", "fastapi", "api"]
)

PYTHON_FLASK = Preset(
    id="python-flask",
    name="Python + Flask",
    description="Python веб-приложение на Flask",
    category="backend",
    icon="🌶️",
    compose_content="""version: '3.8'

services:
  app:
    image: python:3.11-slim
    working_dir: /app
    ports:
      - "${PORT:-5000}:5000"
    volumes:
      - ./app:/app
    command: sh -c "pip install flask && flask run --host=0.0.0.0"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=${FLASK_ENV:-production}
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "5000",
        "FLASK_ENV": "production"
    },
    tags=["python", "flask", "web"]
)

PHP_LARAVEL = Preset(
    id="php-laravel",
    name="PHP + Laravel",
    description="PHP приложение на Laravel фреймворке",
    category="backend",
    icon="🐘",
    compose_content="""version: '3.8'

services:
  app:
    image: php:8.2-fpm-alpine
    working_dir: /var/www
    volumes:
      - ./app:/var/www
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "${PORT:-8080}:80"
    volumes:
      - ./app:/var/www
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "8080",
        "APP_ENV": "production"
    },
    tags=["php", "laravel", "framework"]
)

BACKEND_PRESETS = [NODEJS_EXPRESS, PYTHON_FASTAPI, PYTHON_FLASK, PHP_LARAVEL]

