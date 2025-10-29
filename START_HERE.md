# Start Here - DockLite

**Welcome to DockLite!** 👋

## What is DockLite?

DockLite is a multi-tenant web server management system for deploying docker-compose projects with:
- User isolation and ownership
- Role-based access control
- SSH-based deployment
- Modern web UI

---

## Quick Start (5 minutes)

```bash
# 1. Setup system user
sudo ./docklite setup-user

# 2. Configure SSH
sudo ./docklite setup-ssh

# 3. Start system
./docklite start

# 4. Open browser
http://localhost:5173
```

**Full guide:** [QUICKSTART.md](mdc:QUICKSTART.md)

---

## Documentation

### For Users
- **[QUICKSTART.md](mdc:QUICKSTART.md)** - Fast 5-minute setup
- **[README.md](mdc:README.md)** - Complete user guide
- **[scripts/README.md](mdc:scripts/README.md)** - CLI documentation

### For Developers
- **[ARCHITECTURE.md](mdc:ARCHITECTURE.md)** - System architecture
- **[BACKEND_ARCHITECTURE.md](mdc:BACKEND_ARCHITECTURE.md)** - Backend details
- **[FRONTEND_ARCHITECTURE.md](mdc:FRONTEND_ARCHITECTURE.md)** - Frontend details
- **[PROJECT_STATUS.md](mdc:PROJECT_STATUS.md)** - Current status

### Other Resources
- **[PRESETS.md](mdc:PRESETS.md)** - Available docker-compose presets
- **[SSH_ACCESS.md](mdc:SSH_ACCESS.md)** - SSH deployment guide
- **[DEPLOY_GUIDE.md](mdc:DEPLOY_GUIDE.md)** - Deployment instructions

---

## CLI Commands

DockLite provides a comprehensive CLI:

```bash
# Development
./docklite start            # Start system
./docklite stop             # Stop system
./docklite restart          # Restart
./docklite rebuild          # Rebuild
./docklite status           # Status
./docklite logs             # Logs

# Testing
./docklite test             # All tests
./docklite test-backend     # Backend only
./docklite test-frontend    # Frontend only

# Maintenance
./docklite backup           # Backup
./docklite restore <file>   # Restore
./docklite clean            # Clean resources

# Help
./docklite --help           # Show all commands
./docklite <cmd> --help     # Command-specific help
```

---

## Tech Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy + SQLite
- JWT authentication
- 157 tests

**Frontend:**
- Vue 3 + PrimeVue
- Vite
- 120+ tests

**Infrastructure:**
- Docker + docker-compose
- SSH deployment
- Multi-tenant isolation

---

## Features

✅ Multi-tenancy (user isolation)  
✅ Slug-based project paths  
✅ 14 docker-compose presets  
✅ Container lifecycle management  
✅ Role-based access (admin/user)  
✅ SSH deployment  
✅ Environment variables editor  
✅ 270+ tests with 95% coverage  

---

## Next Steps

1. **Quick Start** - [QUICKSTART.md](mdc:QUICKSTART.md)
2. **Create First Project** - Use UI after setup
3. **Read Architecture** - [ARCHITECTURE.md](mdc:ARCHITECTURE.md)
4. **Explore CLI** - `./docklite --help`

---

## Getting Help

### Built-in Help
```bash
./docklite --help           # Show all commands
./docklite start --help     # Help for specific command
```

### Documentation
- [README.md](mdc:README.md) - Main documentation
- [scripts/README.md](mdc:scripts/README.md) - CLI reference
- [ARCHITECTURE.md](mdc:ARCHITECTURE.md) - Architecture guide

### Troubleshooting

**Docker permission denied:**
```bash
sudo usermod -aG docker $USER
# Then logout and login
```

**SSH not working:**
```bash
sudo ./docklite setup-ssh
ssh docklite@localhost  # Test
```

**Database issues:**
```bash
./docklite init-db --reset
```

---

## Roadmap

**Current:** Phase 3 - Production Ready  
**Next:** Phase 4 - Nginx & Virtual Hosts

See [.cursor/rules/phases-roadmap.mdc](mdc:.cursor/rules/phases-roadmap.mdc) for full roadmap.

---

**Ready to start?** → [QUICKSTART.md](mdc:QUICKSTART.md) 🚀
