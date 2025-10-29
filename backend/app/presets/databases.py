from . import Preset

# Databases

POSTGRESQL = Preset(
    id="postgresql-pgadmin",
    name="PostgreSQL + pgAdmin",
    description="PostgreSQL база данных с веб-интерфейсом pgAdmin",
    category="database",
    icon="🐘",
    compose_content="""version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-mydb}
      - POSTGRES_USER=${POSTGRES_USER:-admin}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4:latest
    expose:
      - "80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=${PGADMIN_EMAIL:-admin@admin.com}
      - PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD:-admin}
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres-data:
""",
    default_env_vars={
        "POSTGRES_DB": "mydb",
        "POSTGRES_USER": "admin",
        "POSTGRES_PASSWORD": "changeme123",
        "PGADMIN_EMAIL": "admin@admin.com",
        "PGADMIN_PASSWORD": "admin123",
    },
    tags=["postgresql", "database", "pgadmin", "traefik"],
)

MYSQL = Preset(
    id="mysql-phpmyadmin",
    name="MySQL + phpMyAdmin",
    description="MySQL база данных с phpMyAdmin",
    category="database",
    icon="🐬",
    compose_content="""version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-rootpass}
      - MYSQL_DATABASE=${MYSQL_DATABASE:-mydb}
      - MYSQL_USER=${MYSQL_USER:-admin}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD:-changeme}
    volumes:
      - mysql-data:/var/lib/mysql
    restart: unless-stopped

  phpmyadmin:
    image: phpmyadmin:latest
    expose:
      - "80"
    environment:
      - PMA_HOST=mysql
      - PMA_PORT=3306
    depends_on:
      - mysql
    restart: unless-stopped

volumes:
  mysql-data:
""",
    default_env_vars={
        "MYSQL_ROOT_PASSWORD": "rootpass123",
        "MYSQL_DATABASE": "mydb",
        "MYSQL_USER": "admin",
        "MYSQL_PASSWORD": "changeme123",
    },
    tags=["mysql", "database", "phpmyadmin", "traefik"],
)

MONGODB = Preset(
    id="mongodb-express",
    name="MongoDB + Mongo Express",
    description="MongoDB NoSQL база с веб-интерфейсом",
    category="database",
    icon="🍃",
    compose_content="""version: '3.8'

services:
  mongodb:
    image: mongo:7
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USER:-admin}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD:-changeme}
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped

  mongo-express:
    image: mongo-express:latest
    expose:
      - "8081"
    environment:
      - ME_CONFIG_MONGODB_ADMINUSERNAME=${MONGO_USER:-admin}
      - ME_CONFIG_MONGODB_ADMINPASSWORD=${MONGO_PASSWORD:-changeme}
      - ME_CONFIG_MONGODB_URL=mongodb://${MONGO_USER:-admin}:${MONGO_PASSWORD:-changeme}@mongodb:27017/
    depends_on:
      - mongodb
    restart: unless-stopped

volumes:
  mongo-data:
""",
    default_env_vars={"MONGO_USER": "admin", "MONGO_PASSWORD": "changeme123"},
    tags=["mongodb", "nosql", "mongo-express", "traefik"],
)

REDIS = Preset(
    id="redis",
    name="Redis",
    description="Redis кеш и очереди сообщений",
    category="database",
    icon="🔴",
    compose_content="""version: '3.8'

services:
  redis:
    image: redis:alpine
    expose:
      - "6379"
    command: redis-server --requirepass ${REDIS_PASSWORD:-changeme}
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
""",
    default_env_vars={"REDIS_PASSWORD": "changeme123"},
    tags=["redis", "cache", "queue"],
)

DATABASE_PRESETS = [POSTGRESQL, MYSQL, MONGODB, REDIS]
