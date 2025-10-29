# System Hostname Support

**Date:** 2025-10-29  
**Feature:** Automatic system hostname detection for access URLs

## Overview

DockLite использует умную логику определения hostname с приоритетами:

### Priority Logic

1. **Config Value** (`HOSTNAME` в .env) - если задано явно
2. **System Hostname** - из `hostname` команды (если валидный)
3. **HTTP Host Header** - из запроса (fallback)
4. **Default** - "localhost"

Это обеспечивает гибкость и надежность в любых условиях.

## Changes Made

### 1. Config Enhancement

**File:** `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # ...
    # Server
    HOSTNAME: Optional[str] = None  # If set, overrides system hostname
```

### 2. Hostname Utility (NEW)

**File:** `backend/app/utils/hostname.py`

```python
def get_server_hostname(fallback: Optional[str] = None) -> str:
    """
    Priority logic:
    1. Config value (settings.HOSTNAME)
    2. System hostname (if valid)
    3. Fallback value or "localhost"
    """
```

**Features:**
- Smart priority logic
- IP address detection (excludes raw IPs)
- Validates hostname quality
- Fallback chain for reliability

### 3. Deployment API Enhancement

**File:** `backend/app/api/deployment.py`

```python
from app.utils.hostname import get_server_hostname

# In endpoints:
server_host = get_server_hostname(fallback=request_host)
```

Deployment instructions теперь используют правильный hostname:

```bash
# Priority 1: Config value
rsync -avz ./app/ docklite@docklite.example.com:/path/

# Priority 2: System hostname
rsync -avz ./app/ docklite@artem.sokolov.me:/path/

# Priority 3: Fallback
rsync -avz ./app/ docklite@localhost:/path/
```

### 4. Status Script Enhancement

**File:** `scripts/maintenance/status.sh`

```bash
# Get system hostname
HOSTNAME=$(hostname)

# Display URLs with hostname
http://artem.sokolov.me
http://artem.sokolov.me/api
http://artem.sokolov.me/docs
http://artem.sokolov.me:8888

# Also show local access
http://localhost
```

### 5. Documentation Updates

**Files Updated:**
- `README.md` - добавлены примеры с hostname
- `TRAEFIK.md` - добавлена секция "System Hostname"
- `HOSTNAME_SUPPORT.md` - полная документация с priority logic

## Configuration Options

### Option 1: Config Value (Recommended for Production)

Create/edit `.env` file:

```bash
# .env
HOSTNAME=docklite.example.com
SECRET_KEY=your-secret-key
```

**Benefits:**
- ✅ Explicit and predictable
- ✅ Independent of system settings
- ✅ Easy to change
- ✅ Works in containers

### Option 2: System Hostname

Set system hostname (used if HOSTNAME not in config):

```bash
# Check current
hostname
# Output: artem.sokolov.me

# Set new
sudo hostnamectl set-hostname your.domain.com

# Verify
hostnamectl
# Static hostname: your.domain.com
```

**Benefits:**
- ✅ System-wide setting
- ✅ Persists across reboots
- ✅ No config needed

### Option 3: Auto-detect (Default)

If neither config nor valid system hostname:
- Uses HTTP Host header from requests
- Falls back to "localhost"

**Use for:** Development on local machine

## Status Output Example

```
╔════════════════════════════════════════════════════════════╗
║ DockLite System Status                                     ║
╚════════════════════════════════════════════════════════════╝

✅ Traefik:  Running
✅ Backend:  Running
✅ Frontend: Running

▶ Access URLs (via Traefik):
ℹ Frontend:          http://artem.sokolov.me
ℹ Backend API:       http://artem.sokolov.me/api
ℹ API Docs:          http://artem.sokolov.me/docs
ℹ Traefik Dashboard: http://artem.sokolov.me:8888
ℹ 
ℹ Local access:      http://localhost
```

## Benefits

1. **Professional URLs** - Shows actual domain instead of "localhost"
2. **Accurate Instructions** - Deployment commands use correct hostname
3. **Easy Sharing** - Team members see correct access URLs
4. **Production Ready** - Works seamlessly with DNS setup

## Use Cases

### Development Server

```bash
# Set hostname
sudo hostnamectl set-hostname dev.company.com

# Status now shows
http://dev.company.com
```

### Production Server

```bash
# Set hostname
sudo hostnamectl set-hostname docklite.company.com

# DNS: A record docklite.company.com → server IP
# Access: http://docklite.company.com
```

### Local Machine

```bash
# Hostname: laptop.local
# Access: http://laptop.local (via mDNS/Avahi)
# Or: http://localhost
```

## Fallback Behavior

If hostname cannot be detected:
- Status script: Shows "localhost"
- Deployment API: Uses HTTP Host header or "your-server"

This ensures system always works even without proper hostname setup.

## Testing

```bash
# 1. Check hostname
hostname

# 2. Run status
./docklite status

# 3. Verify URLs show correct hostname
# ✅ Should display your actual hostname

# 4. Test deployment info API
curl http://localhost/api/deployment/1/info | jq '.server'
# Should return your hostname
```

## Notes

- **Hostname persists across reboots** (set via hostnamectl)
- **DNS not required** for hostname to work locally
- **Works with Traefik** - hostname is just for display
- **Backward compatible** - localhost always works

## Related Documentation

- [TRAEFIK.md](./TRAEFIK.md) - Traefik integration guide
- [README.md](./README.md) - Main documentation
- [DEPLOYMENT.md](./DEPLOY_GUIDE.md) - Deployment guide

---

**Feature Status:** ✅ Complete and Production Ready

