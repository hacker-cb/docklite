from . import Preset

# Web servers and static sites

HELLO_WORLD = Preset(
    id="hello-world",
    name="Hello World (Nginx)",
    description="Минимальный тестовый контейнер с Nginx (дефолтная страница)",
    category="web",
    icon="👋",
    compose_content="""version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "${PORT:-8080}:80"
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "8080"
    },
    tags=["test", "simple", "nginx", "hello"]
)

NGINX_STATIC = Preset(
    id="nginx-static",
    name="Nginx Static Site",
    description="Простой статический сайт на Nginx",
    category="web",
    icon="🌐",
    compose_content="""version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "${PORT:-80}:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "8080"
    },
    tags=["nginx", "static", "simple"]
)

APACHE_STATIC = Preset(
    id="apache-static",
    name="Apache Static Site",
    description="Статический сайт на Apache",
    category="web",
    icon="🪶",
    compose_content="""version: '3.8'

services:
  web:
    image: httpd:alpine
    ports:
      - "${PORT:-80}:80"
    volumes:
      - ./html:/usr/local/apache2/htdocs:ro
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "8081"
    },
    tags=["apache", "static", "simple"]
)

NGINX_PROXY = Preset(
    id="nginx-proxy",
    name="Nginx Reverse Proxy",
    description="Nginx как обратный прокси",
    category="web",
    icon="🔀",
    compose_content="""version: '3.8'

services:
  proxy:
    image: nginx:alpine
    ports:
      - "${PORT:-80}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    restart: unless-stopped
""",
    default_env_vars={
        "PORT": "80",
        "BACKEND_URL": "http://backend:3000"
    },
    tags=["nginx", "proxy", "reverse-proxy"]
)

WEB_PRESETS = [HELLO_WORLD, NGINX_STATIC, APACHE_STATIC, NGINX_PROXY]

