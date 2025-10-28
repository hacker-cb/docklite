from . import Preset

# CMS and ready solutions

WORDPRESS = Preset(
    id="wordpress",
    name="WordPress",
    description="Популярная CMS для блогов и сайтов",
    category="cms",
    icon="📝",
    compose_content="""version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "${PORT:-8080}:80"
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=${DB_USER:-wordpress}
      - WORDPRESS_DB_PASSWORD=${DB_PASSWORD:-changeme}
      - WORDPRESS_DB_NAME=${DB_NAME:-wordpress}
    volumes:
      - wordpress-data:/var/www/html
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=${DB_NAME:-wordpress}
      - MYSQL_USER=${DB_USER:-wordpress}
      - MYSQL_PASSWORD=${DB_PASSWORD:-changeme}
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-rootpass}
    volumes:
      - db-data:/var/lib/mysql
    restart: unless-stopped

volumes:
  wordpress-data:
  db-data:
""",
    default_env_vars={
        "PORT": "8080",
        "DB_NAME": "wordpress",
        "DB_USER": "wordpress",
        "DB_PASSWORD": "changeme123",
        "DB_ROOT_PASSWORD": "rootpass123"
    },
    tags=["wordpress", "cms", "php", "mysql"]
)

GHOST = Preset(
    id="ghost",
    name="Ghost",
    description="Современная платформа для блогов",
    category="cms",
    icon="👻",
    compose_content="""version: '3.8'

services:
  ghost:
    image: ghost:alpine
    ports:
      - "${PORT:-2368}:2368"
    environment:
      - url=http://localhost:${PORT:-2368}
      - database__client=mysql
      - database__connection__host=db
      - database__connection__user=${DB_USER:-ghost}
      - database__connection__password=${DB_PASSWORD:-changeme}
      - database__connection__database=${DB_NAME:-ghost}
    volumes:
      - ghost-data:/var/lib/ghost/content
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=${DB_NAME:-ghost}
      - MYSQL_USER=${DB_USER:-ghost}
      - MYSQL_PASSWORD=${DB_PASSWORD:-changeme}
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-rootpass}
    volumes:
      - db-data:/var/lib/mysql
    restart: unless-stopped

volumes:
  ghost-data:
  db-data:
""",
    default_env_vars={
        "PORT": "2368",
        "DB_NAME": "ghost",
        "DB_USER": "ghost",
        "DB_PASSWORD": "changeme123",
        "DB_ROOT_PASSWORD": "rootpass123"
    },
    tags=["ghost", "blog", "cms", "nodejs"]
)

STRAPI = Preset(
    id="strapi",
    name="Strapi",
    description="Headless CMS на Node.js",
    category="cms",
    icon="🚀",
    compose_content="""version: '3.8'

services:
  strapi:
    image: strapi/strapi:latest
    ports:
      - "${PORT:-1337}:1337"
    environment:
      - DATABASE_CLIENT=postgres
      - DATABASE_HOST=db
      - DATABASE_PORT=5432
      - DATABASE_NAME=${DB_NAME:-strapi}
      - DATABASE_USERNAME=${DB_USER:-strapi}
      - DATABASE_PASSWORD=${DB_PASSWORD:-changeme}
    volumes:
      - strapi-data:/srv/app
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${DB_NAME:-strapi}
      - POSTGRES_USER=${DB_USER:-strapi}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-changeme}
    volumes:
      - db-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  strapi-data:
  db-data:
""",
    default_env_vars={
        "PORT": "1337",
        "DB_NAME": "strapi",
        "DB_USER": "strapi",
        "DB_PASSWORD": "changeme123"
    },
    tags=["strapi", "headless-cms", "nodejs", "api"]
)

CMS_PRESETS = [WORDPRESS, GHOST, STRAPI]

