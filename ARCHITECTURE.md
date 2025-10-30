# DockLite - System Architecture

**Status:** Production Ready

## Overview

DockLite is a multi-tenant web server management system for deploying multiple docker-compose projects with user isolation, role-based access control, and SSH-based deployment.

## Core Concepts

### Multi-Tenancy

DockLite implements true multi-tenant architecture:

**User Isolation:**
- Each DockLite user maps to a Linux system user
- Projects are stored in `/home/{system_user}/projects/`
- SSH operations run under the system user context
- Role-based access: users see only their projects, admins see all

**Project Ownership:**
- Every project has an `owner_id` (FK to users)
- Slug-based paths: `example-com-a7b2` instead of numeric IDs
- Slugs generated from domain + short hash

**Benefits:**
- System-level isolation between users
- Clear ownership and permissions
- Readable, meaningful paths
- Scalable architecture

---

## Technology Stack

### Backend (Python/FastAPI)

**Core:**
- FastAPI - Async web framework
- SQLAlchemy 2.0 - ORM with async support
- Alembic - Database migrations
- Pydantic - Data validation

**Auth & Security:**
- JWT tokens (python-jose)
- Bcrypt password hashing (passlib)
- Role-based access control

**Deployment:**
- SSH via subprocess
- docker-compose orchestration
- PyYAML for validation

**Testing:**
- Pytest (157 tests, 95% coverage)
- AsyncIO test support
- Integration tests

### Frontend (Vue.js 3)

**Core:**
- Vue 3 Composition API
- Vue Router 4 (history mode)
- PrimeVue UI components
- Vite build tool

**State & API:**
- Axios HTTP client
- Composables for state management
- RESTful API integration

**Testing:**
- Vitest (120+ tests)
- Vue Test Utils
- Component testing

### Infrastructure

**Database:**
- SQLite (default)
- PostgreSQL ready
- Async connections

**Containerization:**
- Docker for DockLite itself
- docker-compose for orchestration
- Multi-stage builds

**Deployment:**
- SSH-based (per system user)
- rsync/scp/SFTP support
- Linux user isolation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DockLite System                          │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │◄───────►│   Backend    │                 │
│  │  Vue 3 SPA   │  HTTP   │   FastAPI    │                 │
│  │  PrimeVue UI │         │   SQLAlchemy │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
│                          ┌────────▼────────┐                │
│                          │    SQLite DB    │                │
│                          │  users/projects │                │
│                          └─────────────────┘                │
└───────────────────────────────┬──────────────────────────────┘
                                │ SSH
                    ┌───────────▼───────────┐
                    │   System Users        │
                    │  (docklite, user1...) │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
   ┌────▼────┐                                    ┌────▼────┐
   │ User 1  │                                    │ User 2  │
   │ Projects│                                    │ Projects│
   │         │                                    │         │
   │ project1│                                    │ project3│
   │ project2│                                    │ project4│
   └─────────┘                                    └─────────┘
```

---

## Database Schema

### Core Tables

**users** - DockLite users
```sql
id              INTEGER PRIMARY KEY
username        VARCHAR(255) UNIQUE NOT NULL
email           VARCHAR(255) UNIQUE
password_hash   VARCHAR(255) NOT NULL
system_user     VARCHAR(255) NOT NULL DEFAULT 'docklite'
is_active       INTEGER DEFAULT 1
is_admin        INTEGER DEFAULT 0
created_at      DATETIME
updated_at      DATETIME
```

**projects** - User projects
```sql
id              INTEGER PRIMARY KEY
name            VARCHAR(255) NOT NULL
domain          VARCHAR(255) UNIQUE NOT NULL
slug            VARCHAR(255) UNIQUE NOT NULL
owner_id        INTEGER NOT NULL REFERENCES users(id)
compose_content TEXT NOT NULL
env_vars        TEXT DEFAULT '{}'
status          VARCHAR(50) DEFAULT 'created'
created_at      DATETIME
updated_at      DATETIME
```

### Relationships

- `User` ─< 1:N >─ `Project` (one user, many projects)
- Projects filtered by ownership (non-admin users)
- Cascade delete on user removal (optional)

---

## API Architecture

### RESTful Endpoints

**Authentication:**
- `POST /api/auth/login` - JWT login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/setup` - Initial admin setup
- `GET /api/auth/setup/check` - Check if setup needed
- `GET /api/auth/me` - Current user info

**Users (Admin only):**
- `GET /api/users` - List all users
- `POST /api/users` - Create user (with system_user)
- `GET /api/users/{id}` - Get user
- `PATCH /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/password` - Change password

**Projects:**
- `GET /api/projects` - List projects (filtered by ownership)
- `POST /api/projects` - Create project (current user is owner)
- `GET /api/projects/{id}` - Get project (ownership check)
- `PUT /api/projects/{id}` - Update project (ownership check)
- `DELETE /api/projects/{id}` - Delete project (ownership check)

**Environment:**
- `GET /api/projects/{id}/env` - Get env vars
- `PUT /api/projects/{id}/env` - Update env vars

**Containers:**
- `POST /api/containers/{id}/start` - Start containers
- `POST /api/containers/{id}/stop` - Stop containers
- `POST /api/containers/{id}/restart` - Restart containers
- `GET /api/containers/{id}/status` - Get status

**Deployment:**
- `GET /api/deployment/{id}/info` - Deployment instructions

**Presets:**
- `GET /api/presets` - List all presets
- `GET /api/presets/categories` - List categories
- `GET /api/presets/{id}` - Get preset template

### Authentication Flow

```
1. User → POST /api/auth/login {username, password}
2. Backend validates credentials
3. Backend generates JWT token
4. Frontend stores token in localStorage
5. All subsequent requests include: Authorization: Bearer {token}
6. Backend validates token on protected endpoints
```

### Authorization

**Ownership Check:**
```python
# Non-admin users can only access their own projects
project = await service.get_project(
    project_id, 
    user_id=current_user.id,
    is_admin=current_user.is_admin
)
```

**Admin Privileges:**
- View all users and projects
- Manage all resources
- No ownership restrictions

---

## Deployment Flow

### SSH-Based Deployment

**1. Project Creation:**
```
User creates project in UI
  ↓
Backend generates slug from domain
  ↓
Backend creates directory: /home/{system_user}/projects/{slug}/
  ↓
Backend writes docker-compose.yml and .env
  ↓
Project status: "created"
```

**2. Container Management:**
```
User clicks "Start" in UI
  ↓
Backend SSH to: {system_user}@localhost
  ↓
Execute: cd /home/{system_user}/projects/{slug} && docker-compose up -d
  ↓
Update project status: "running"
```

**3. File Upload (via SSH):**
```bash
# User can upload files via:
rsync -avz ./files/ {system_user}@server:/home/{system_user}/projects/{slug}/
scp -r ./files/ {system_user}@server:/home/{system_user}/projects/{slug}/
```

---

## Security

### Authentication
- JWT tokens with expiration
- Bcrypt password hashing (cost factor 12)
- Token validation on every request
- Secure password requirements

### Authorization
- Role-based access (admin vs user)
- Ownership checks on all resources
- System user isolation

### SSH Security
- Key-based authentication only
- Per-user SSH access
- No root access
- Isolated home directories

### Docker Security
- Non-root containers
- Resource limits (planned)
- Network isolation (planned)

---

## File Structure

### DockLite System

```
~/docklite/
├── backend/
│   ├── app/
│   │   ├── api/           # REST endpoints
│   │   ├── services/      # Business logic
│   │   ├── models/        # DB models
│   │   ├── core/          # Config, auth, DB
│   │   ├── constants/     # Enums, messages
│   │   ├── exceptions/    # Custom exceptions
│   │   ├── utils/         # Formatters, responses
│   │   ├── validators/    # Validation logic
│   │   └── presets/       # 14 templates
│   ├── alembic/           # DB migrations
│   ├── tests/             # 157 tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Dialogs
│   │   ├── views/         # Pages
│   │   ├── composables/   # Reusable logic
│   │   ├── config/        # Constants
│   │   ├── utils/         # Helpers
│   │   ├── App.vue
│   │   ├── router.js
│   │   └── api.js
│   ├── tests/             # 120+ tests
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

### User Projects

```
/home/{system_user}/projects/
├── example-com-a7b2/          # Project slug
│   ├── docker-compose.yml     # Container config
│   ├── .env                   # Environment vars
│   └── [project files]        # Uploaded files
└── mysite-org-c3d9/
    ├── docker-compose.yml
    └── .env
```

---

## Testing

### Backend Tests (157 total)

**API Tests (60+):**
- Authentication flow
- CRUD operations
- Ownership checks
- Error handling

**Service Tests (25+):**
- Business logic
- Data validation
- Database operations

**Validator Tests (24):**
- docker-compose validation
- Domain validation

**Utils Tests (42):**
- Formatters
- Response builders
- Logging

**Integration Tests (7):**
- Full lifecycle
- SSH operations
- Container management

### Frontend Tests (120+)

**Component Tests (40+):**
- Dialog interactions
- Form validation
- Props & events

**View Tests (25+):**
- Projects page
- Users page
- Navigation

**Composable Tests (30+):**
- API integration
- State management
- Error handling

**Utils Tests (20+):**
- Formatters
- Toast notifications

**Router Tests (8+):**
- Navigation guards
- Route definitions

---

## Deployment Guide

### Initial Setup

1. **Create system user:**
```bash
sudo useradd -m -s /bin/bash docklite
sudo usermod -aG docker docklite
```

2. **Setup SSH:**
```bash
sudo -u docklite ssh-keygen -t ed25519
# Add public key to authorized_keys
```

3. **Deploy DockLite:**
```bash
cd ~/docklite
docker-compose up -d
```

4. **Create admin user:**
- Navigate to http://server:5173
- Fill in setup form (username, email, system_user, password)
- Login and start creating projects

### Adding Users

**Via UI (Admin only):**
1. Login as admin
2. Go to Users page
3. Click "New User"
4. Fill in: username, email, **system_user**, password
5. User can now login and create projects

**System user must exist:**
```bash
# Create Linux user for new DockLite user
sudo useradd -m -s /bin/bash newuser
sudo usermod -aG docker newuser
```

---

## Best Practices

### Development

- ✅ Use type hints (Python) and JSDoc (JavaScript)
- ✅ Write tests for new features
- ✅ Follow existing code patterns
- ✅ Use constants, never magic strings
- ✅ Validate all inputs
- ✅ Handle errors gracefully

### Security

- ✅ Never commit secrets
- ✅ Use strong passwords
- ✅ Rotate JWT secrets
- ✅ Keep dependencies updated
- ✅ Review SSH access regularly
- ✅ Monitor logs

### Operations

- ✅ Backup database regularly
- ✅ Monitor disk usage
- ✅ Set up log rotation
- ✅ Test backups periodically
- ✅ Document custom changes
- ✅ Version control everything

---

## Current Status & Roadmap

### ✅ Phase 4: Traefik Integration (COMPLETE)
- Traefik v3 reverse proxy on port 80/443
- Automatic service discovery via Docker labels
- Domain-based routing (no ports!)
- Auto-inject Traefik labels on project create/update
- Shared `docklite-network` for all services
- Admin-only dashboard with ForwardAuth

### Phase 5: SSL/HTTPS (Next - 90% Ready)
- Let's Encrypt integration
- Automatic certificate generation
- Auto-renewal with Traefik built-in resolver
- HTTPS by default
- HTTP → HTTPS redirect

### Phase 6: Logs Management
- View container logs in UI
- Real-time log streaming
- Log search and filtering
- Log retention policies

### Phase 7: MCP Server
- AI agent integration
- Project management via AI
- Natural language commands
- Automated deployments

---

## Performance

### Current Stats

**Backend:**
- Response time: <100ms (local)
- Database: SQLite (fast for <1000 projects)
- Tests: 157 in ~45s

**Frontend:**
- Build time: ~15s
- Bundle size: ~500KB gzipped
- First paint: <1s

**Scalability:**
- Tested: 100+ projects
- Recommended: <500 projects per instance
- Migration to PostgreSQL for larger deployments

---

## Conclusion

DockLite provides a production-ready, multi-tenant platform for managing docker-compose deployments with:

✅ User isolation and ownership  
✅ Clean architecture and best practices  
✅ Comprehensive test coverage  
✅ Modern tech stack  
✅ Secure by design  

**Status:** Production Ready for small to medium deployments

