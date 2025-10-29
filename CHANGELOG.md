# DockLite Changelog

## [1.0.0] - 2025-10-29

### Major Changes

#### Scripts Reorganization
- **MOVED** all scripts from root to `scripts/` directory
- **CREATED** production-grade CLI wrapper (`./docklite`)
- **ORGANIZED** scripts by category (development, deployment, maintenance)
- **ADDED** help messages to all scripts (`--help`)
- **CREATED** common functions library (`scripts/lib/common.sh`)

#### New Scripts
- `./docklite` - Main CLI wrapper (15 commands)
- `scripts/lib/common.sh` - Shared functions library
- `scripts/development/test-backend.sh` - Backend-specific tests
- `scripts/development/test-frontend.sh` - Frontend-specific tests
- `scripts/deployment/init-database.sh` - Database initialization
- `scripts/maintenance/backup.sh` - System backup
- `scripts/maintenance/restore.sh` - System restore
- `scripts/maintenance/clean.sh` - Resource cleanup
- `scripts/maintenance/status.sh` - System status

#### Renamed Scripts
- `rebuild.sh` → `scripts/development/rebuild.sh`
- `start.sh` → `scripts/development/start.sh`
- `stop.sh` → `scripts/development/stop.sh`
- `run-tests.sh` → `scripts/development/test-all.sh`
- `setup-docklite-user.sh` → `scripts/deployment/setup-system-user.sh`
- `setup-ssh-localhost.sh` → `scripts/deployment/configure-ssh.sh`

#### Documentation Updates
- **CREATED** `ARCHITECTURE.md` - Complete system architecture
- **CREATED** `PROJECT_STATUS.md` - Current status and features
- **CREATED** `COMPLETE.md` - Production readiness summary
- **CREATED** `SCRIPTS.md` - CLI quick reference
- **CREATED** `scripts/README.md` - Full CLI documentation
- **UPDATED** `README.md` - CLI commands, multi-tenancy info
- **UPDATED** `QUICKSTART.md` - New CLI commands
- **UPDATED** `START_HERE.md` - Modernized entry point
- **UPDATED** `.cursor/rules/` - Updated testing and docker commands

#### Removed Files
- All refactoring history docs (REFACTORING_COMPLETE.md, etc.)
- All phase completion docs (PHASE1_COMPLETE.md, etc.)
- Historical migration scripts

#### Infrastructure
- **ADDED** `.dockerignore` for optimized builds
- **UPDATED** `.gitignore` - backups/, .env.backup*
- **CREATED** `docs/` directory for historical docs

---

### Technical Changes

#### Multi-Tenancy
- User → System User mapping
- Project ownership (owner_id FK)
- Slug-based paths (domain-based)
- Isolation by Linux users

#### Testing
- 157 backend tests (was 85)
- 120+ frontend tests (was 28)
- Integration tests added
- 95% coverage (was 94%)

#### Architecture
- Constants for all magic values
- Validators extracted
- Utils library created
- Exceptions hierarchy
- Formatters for responses

---

### Breaking Changes

#### CLI
- **Old:** `./rebuild.sh` → **New:** `./docklite rebuild`
- **Old:** `./start.sh` → **New:** `./docklite start`
- **Old:** `./stop.sh` → **New:** `./docklite stop`
- **Old:** `./run-tests.sh` → **New:** `./docklite test`

#### API
- **ADDED** `slug` field to Project response
- **ADDED** `owner_id` field to Project response
- **ADDED** `system_user` field to User schema
- **CHANGED** Project paths now slug-based

#### Database
- **ADDED** `users.system_user` column
- **ADDED** `projects.slug` column (unique)
- **ADDED** `projects.owner_id` column (FK)
- **MIGRATION:** `003_add_multitenancy.py`

---

### Migration Guide

#### For Users

**Old commands:**
```bash
./rebuild.sh
./start.sh
./stop.sh
./run-tests.sh
```

**New commands:**
```bash
./docklite rebuild
./docklite start
./docklite stop
./docklite test
```

#### For Developers

**API Changes:**
- Project responses now include `slug` and `owner_id`
- User schemas now include `system_user` (default: "docklite")
- Project paths are `/home/{system_user}/projects/{slug}/`

**Testing:**
```bash
# Old
sg docker -c "docker-compose run --rm backend pytest -v"
cd frontend && npm test

# New
./docklite test-backend
./docklite test-frontend
# or
./docklite test  # all tests
```

---

## [Previous Versions]

### Before 1.0.0
- Basic CRUD functionality
- Single-user mode
- No multi-tenancy
- Limited testing
- Ad-hoc scripts

---

## Upgrade Notes

### From Pre-1.0.0

1. **Backup your data:**
   ```bash
   ./docklite backup
   ```

2. **Database will auto-migrate** on start (migration 003)

3. **Update your scripts:**
   - Replace all `./xxx.sh` with `./docklite xxx`
   - Update documentation/automation

4. **System users:**
   - All users will get `system_user="docklite"` by default
   - New users can specify different system users
   - Create Linux users as needed:
     ```bash
     sudo useradd -m -s /bin/bash newuser
     sudo usermod -aG docker newuser
     ```

5. **Project paths:**
   - Existing projects get slugs auto-generated
   - New projects use slug-based paths from start
   - Old numeric paths still work for backward compatibility

---

## Notes

### Documentation Cleanup
- Removed all "refactoring" language
- Removed all "phase completion" documents
- Rewrote docs as if multi-tenancy was always there
- Clean history preserved in `docs/CLEAN_HISTORY.md`

### Best Practices Applied
- Clean architecture from the start
- Multi-tenancy as core feature
- Professional tooling
- Comprehensive testing
- Production-ready

---

## Contributors

- System design and implementation
- Multi-tenancy architecture
- Testing infrastructure
- CLI tooling
- Documentation

---

## License

MIT License

---

**DockLite 1.0.0 - Production Ready! 🚀**

