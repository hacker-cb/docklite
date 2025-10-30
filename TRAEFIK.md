# Traefik Integration Guide

## Overview

DockLite uses **Traefik v3** as a modern cloud-native reverse proxy for automatic service discovery and routing. Traefik eliminates the need for manual port management by automatically routing traffic based on domain names.

## Key Features

- **Automatic Service Discovery** - Traefik automatically detects project containers via Docker labels
- **Domain-Based Routing** - Access projects by domain without port numbers (`http://example.com` instead of `http://example.com:8080`)
- **Zero Downtime** - Dynamic configuration updates without reloads
- **SSL Ready** - Infrastructure prepared for Let's Encrypt integration (Phase 5)
- **Dashboard** - Web UI for monitoring routes and services

## Architecture

### How It Works

```
User Request (http://example.com)
         ↓
    Traefik (Port 80/443)
         ↓
  Reads Docker Labels
         ↓
Routes to Project Container
    (Internal Network)
```

### Network Configuration

- **docklite-network**: Shared Docker network for all DockLite components
- All project containers are automatically connected to `docklite-network`
- Traefik monitors containers on this network for label changes

## Traefik Configuration

### Main Container

Location: `docker-compose.yml`

```yaml
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"        # HTTP traffic
      - "443:443"      # HTTPS traffic (ready for SSL)
      - "8888:8080"    # Traefik Dashboard
    command:
      - "--api.dashboard=true"
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=docklite-network"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - docklite-network
```

**Important:** Port 8888 is used for the Traefik dashboard to avoid conflicts with backend API (port 8000).

### Project Labels

When you create a project, DockLite automatically injects Traefik labels into the `docker-compose.yml`:

```yaml
services:
  app:
    image: your-image
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.example-com-1.rule=Host(`example.com`)"
      - "traefik.http.routers.example-com-1.entrypoints=web"
      - "traefik.http.services.example-com-1.loadbalancer.server.port=80"
    networks:
      - docklite-network

networks:
  docklite-network:
    external: true
```

**Label Explanation:**

- `traefik.enable=true` - Enables Traefik routing for this container
- `traefik.http.routers.{slug}.rule=Host(...)` - Defines routing rule (by domain)
- `traefik.http.routers.{slug}.entrypoints=web` - Uses HTTP entrypoint (port 80)
- `traefik.http.services.{slug}.loadbalancer.server.port=...` - Internal container port

## Traefik Dashboard

Access the Traefik dashboard to monitor routes and services:

```
http://localhost:8888
```

**Features:**
- View all active routes
- Monitor service health
- See real-time traffic
- Debug routing issues

## Port Detection

DockLite automatically detects the internal port from your `docker-compose.yml`:

### From `expose` Section
```yaml
services:
  web:
    image: nginx:alpine
    expose:
      - "80"  # ← Detected as internal port
```

### From `ports` Section
```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"  # ← Extracts 80 as internal port
```

### Default
If no port is specified, defaults to **80**.

## Multi-Service Projects

For projects with multiple services (e.g., WordPress + MySQL):

- Traefik labels are added to the **first service** only (the web-facing service)
- Other services (databases, caches) remain internal to the Docker network
- Example: WordPress project exposes WordPress container via Traefik, MySQL stays internal

## Custom Domains Setup

### System Hostname

DockLite automatically uses your system hostname for access URLs. Check your hostname:

```bash
hostname
# Output: example.com (example)
```

To set/change hostname:

```bash
sudo hostnamectl set-hostname your.domain.com
```

### Development (localhost)

For local development, you can use `/etc/hosts` to map domains:

```bash
# /etc/hosts
127.0.0.1  example.com
127.0.0.1  myapp.local
```

Then access projects:
- `http://example.com`
- `http://myapp.local`

### Production

1. **Configure DNS** - Point your domain A record to server IP
2. **Create Project** - Use your domain name in DockLite
3. **Deploy Files** - Upload project files via SSH
4. **Start Container** - Run `docker-compose up -d`
5. **Access** - Visit `http://yourdomain.com`

## SSL/HTTPS (Coming in Phase 5)

Infrastructure is ready for SSL/HTTPS with Let's Encrypt:

```yaml
# Future configuration example
labels:
  - "traefik.http.routers.example.tls=true"
  - "traefik.http.routers.example.tls.certresolver=letsencrypt"
```

Features planned:
- Automatic SSL certificate generation
- Auto-renewal
- HTTP to HTTPS redirect
- Wildcard certificates support

## Troubleshooting

### Project not accessible

1. **Check Traefik Dashboard** (`http://localhost:8888`)
   - Is the route registered?
   - Is the service healthy?

2. **Verify Docker Labels**
   ```bash
   cd /home/{user}/projects/{slug}
   grep -A 5 "labels:" docker-compose.yml
   ```

3. **Check Container Network**
   ```bash
   docker inspect <container-name> | grep -A 10 Networks
   ```
   
   Should include `docklite-network`

4. **View Traefik Logs**
   ```bash
   docker logs docklite-traefik
   ```

### Port Conflicts

If you see "port already allocated" errors:

- Port 80: Check if Apache/Nginx is running on host
- Port 443: Check for existing HTTPS services
- Port 8888: Change dashboard port in `docker-compose.yml`

```bash
# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

### DNS Resolution

If domain doesn't resolve:

1. **Check /etc/hosts** (local development)
2. **Check DNS records** (production)
3. **Test with curl**
   ```bash
   curl -H "Host: example.com" http://localhost
   ```

## Migration from Port-Based Routing

Existing projects with port mappings will be automatically updated:

1. **On Create** - New projects get Traefik labels automatically
2. **On Update** - Existing projects are updated when docker-compose is modified
3. **Ports Removed** - `ports:` section is removed, replaced with `expose:`
4. **Labels Added** - Traefik routing labels are injected

**Note:** Projects created before Traefik integration will continue to work. To migrate them:
- Edit project in UI
- Save changes
- Restart container

## API Integration

### TraefikService

Location: `backend/app/services/traefik_service.py`

**Methods:**

```python
from app.services.traefik_service import TraefikService

# Generate labels
labels = TraefikService.generate_labels(
    domain="example.com",
    slug="example-com-1",
    internal_port=80
)

# Inject labels into compose
modified, error = TraefikService.inject_labels_to_compose(
    compose_content=original_yaml,
    domain="example.com",
    slug="example-com-1"
)

# Detect internal port
port = TraefikService.detect_internal_port(compose_content)
```

### Automatic Injection

ProjectService automatically calls TraefikService:

- **On Create**: Injects labels into new projects
- **On Update**: Re-injects labels when compose or domain changes

## Best Practices

1. **Use Clear Domain Names** - Choose descriptive domains for easy identification
2. **One Service Per Port** - Avoid multiple services on same port
3. **Use Expose, Not Ports** - Let Traefik handle external access
4. **Keep Internal Services Internal** - Databases don't need Traefik routing
5. **Monitor Dashboard** - Regularly check Traefik dashboard for issues

## Advanced Configuration

### Custom Entry Points

For custom protocols or ports:

```yaml
labels:
  - "traefik.http.routers.myapp.entrypoints=custom"
  - "traefik.http.routers.myapp.rule=Host(`example.com`)"
```

### Middleware

Add authentication, rate limiting, or redirects:

```yaml
labels:
  - "traefik.http.middlewares.auth.basicauth.users=user:password"
  - "traefik.http.routers.myapp.middlewares=auth"
```

### Load Balancing

For scaled services:

```yaml
services:
  app:
    image: myapp
    deploy:
      replicas: 3
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`example.com`)"
```

## Resources

- **Traefik Documentation**: https://doc.traefik.io/traefik/
- **Docker Provider**: https://doc.traefik.io/traefik/providers/docker/
- **Routing Rules**: https://doc.traefik.io/traefik/routing/routers/

## Next Steps

After Traefik integration:

- **Phase 5**: SSL/HTTPS with Let's Encrypt
- **Phase 6**: Log viewing in UI
- **Phase 7**: Health checks and monitoring

---

**Questions?** Check the main [README.md](./README.md) or open an issue.

