# DockLite - Quick Start Guide

Fast setup guide for DockLite.

## Prerequisites

- Linux server (Ubuntu/Debian)
- Docker installed
- sudo access

## Installation (5 minutes)

### 1. Setup System User

```bash
cd ~/docklite
sudo ./docklite deploy setup-user
```

Creates `docklite` Linux user for deployment.

### 2. Configure SSH

```bash
sudo ./docklite deploy setup-ssh
```

Sets up SSH keys for localhost deployment.

### 3. Install Bash Completion (Optional)

```bash
./docklite install-completion
source ~/.bashrc
```

Enables Tab auto-completion for all commands!

### 4. Start DockLite

```bash
./docklite start
```

### 5. Access UI

Open: **http://localhost:5173**

### 6. Create Admin

Fill in the setup form:
- Username
- Email (optional)
- System User: `docklite`
- Password

Click "Create Admin Account"

---

## Create Your First Project

### Option 1: From Preset (Recommended)

1. Click "New Project"
2. Select "From Preset"
3. Choose preset (e.g., Nginx, WordPress)
4. Fill in Name and Domain
5. Click "Create"
6. Click "Start" to launch containers

### Option 2: Custom docker-compose

1. Click "New Project"
2. Select "Custom Compose"
3. Fill in Name, Domain, and docker-compose.yml content
4. Click "Create"

---

## Useful Commands

```bash
./docklite status                # Check system status
./docklite logs                  # View logs
./docklite test                  # Run tests
./docklite maint backup          # Create backup
./docklite --help                # Show all commands
./docklite user list             # List users
./docklite user add newuser      # Add new user
```

---

## Forgot Password?

```bash
./docklite user reset-password admin     # Reset admin password
```

---

## Next Steps

- Read [README.md](mdc:README.md) for detailed guide
- Check [SCRIPTS.md](mdc:SCRIPTS.md) for all CLI commands
- See [ARCHITECTURE.md](mdc:ARCHITECTURE.md) for system architecture
- Install completion: `./docklite install-completion`

---

## Troubleshooting

### Docker permission denied
```bash
sudo usermod -aG docker $USER
# Then logout and login again
```

### Can't connect to SSH
```bash
sudo ./docklite deploy setup-ssh  # Re-run SSH setup
ssh docklite@localhost            # Test connection
```

### Forgot password
```bash
./docklite user reset-password admin  # Reset password
```

### Database issues
```bash
./docklite deploy init-db --reset  # Reset database (WARNING: deletes data!)
```

---

**That's it!** DockLite is ready to use 🚀
