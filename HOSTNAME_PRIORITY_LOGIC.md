# Hostname Priority Logic - Implementation Complete

**Date:** 2025-10-29  
**Feature:** Smart hostname detection with configurable priority  
**Status:** ✅ Production Ready

## Overview

Реализована умная система определения hostname с гибкими приоритетами, позволяющая точно контролировать как система определяет свой адрес для отображения URL и deployment инструкций.

## Priority Chain

```
┌─────────────────────────────────────────┐
│  1. Config Value (settings.HOSTNAME)    │ ← Highest Priority
├─────────────────────────────────────────┤
│  2. System Hostname (socket.hostname()) │ ← If valid
├─────────────────────────────────────────┤
│  3. HTTP Host Header (from request)     │ ← Fallback
├─────────────────────────────────────────┤
│  4. Default ("localhost")               │ ← Last Resort
└─────────────────────────────────────────┘
```

## Implementation

### Core Utility

**File:** `backend/app/utils/hostname.py`

```python
def get_server_hostname(fallback: Optional[str] = None) -> str:
    """
    Get server hostname with priority logic:
    
    Priority 1: Config value (settings.HOSTNAME)
    Priority 2: System hostname (if valid)
    Priority 3: Fallback value
    Priority 4: "localhost"
    """
```

**Validation Logic:**
- ✅ Checks if hostname is not empty
- ✅ Excludes "localhost" from system hostname
- ✅ Excludes raw IP addresses (e.g., "192.168.1.1")
- ✅ Validates hostname quality

### Config Support

**File:** `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # ...
    HOSTNAME: Optional[str] = None  # Overrides system hostname
```

**Usage in .env:**

```bash
# .env
HOSTNAME=docklite.example.com
```

### Integration Points

#### 1. Deployment API

```python
# backend/app/api/deployment.py
from app.utils.hostname import get_server_hostname

server_host = get_server_hostname(fallback=request_host)
```

**Result:** Deployment instructions показывают правильный hostname во всех командах

#### 2. Status Script

```bash
# scripts/maintenance/status.sh
HOSTNAME=$(hostname)

# Shows:
http://artem.sokolov.me
http://artem.sokolov.me/api
```

## Use Cases

### Production Server

```bash
# .env
HOSTNAME=docklite.company.com

# Result:
# - All URLs show docklite.company.com
# - Independent of system hostname
# - Predictable and explicit
```

### Development Server

```bash
# Set system hostname
sudo hostnamectl set-hostname dev.company.local

# No .env HOSTNAME needed
# Uses system hostname automatically
```

### Local Development

```bash
# No configuration needed
# Falls back to localhost
# Works out of the box
```

### Docker/Container

```bash
# .env
HOSTNAME=docklite.example.com

# System hostname in container is random
# But config value takes priority
# Reliable in any environment
```

## Configuration Guide

### Option 1: Config (Recommended)

**Best for:** Production, containers, explicit control

```bash
# Create .env
cat > .env << 'EOF'
SECRET_KEY=your-secret-key
HOSTNAME=docklite.example.com
EOF

# Restart
./docklite restart
```

**Pros:**
- ✅ Explicit and predictable
- ✅ Works in containers
- ✅ Easy to change
- ✅ Version controlled (if desired)

### Option 2: System Hostname

**Best for:** Traditional servers, simple setups

```bash
# Set hostname
sudo hostnamectl set-hostname artem.sokolov.me

# Verify
hostname
# artem.sokolov.me

# No .env change needed
./docklite restart
```

**Pros:**
- ✅ System-wide setting
- ✅ Persists across reboots
- ✅ No config file needed

### Option 3: Auto-detect

**Best for:** Development, testing

```bash
# No configuration
# Uses HTTP Host header or localhost
# Works immediately
```

## Validation Rules

Hostname utility validates system hostname:

### ✅ Valid Hostnames
```
example.com
subdomain.example.com
artem.sokolov.me
server-01.internal
```

### ❌ Invalid (Skipped)
```
localhost           # Too generic
192.168.1.1        # Raw IP address
10.0.0.1          # Raw IP address
                  # Empty string
   (whitespace)   # Only whitespace
```

## Testing

### Unit Tests

**File:** `backend/tests/test_utils/test_hostname.py`

```bash
# Run tests
./docklite test-backend -k test_hostname

# Expected: All tests pass
# ✅ Priority logic
# ✅ IP validation
# ✅ URL generation
# ✅ Edge cases
```

### Manual Testing

```bash
# 1. Test with config
echo "HOSTNAME=test.example.com" >> .env
./docklite restart
./docklite status
# Should show: http://test.example.com

# 2. Test without config
# Remove HOSTNAME from .env
./docklite restart
./docklite status
# Should show system hostname

# 3. Test API
curl http://localhost/api/deployment/ssh-setup | jq '.server'
# Should return detected hostname
```

## Benefits

### 1. Flexibility
- ✅ Multiple configuration methods
- ✅ Automatic fallback chain
- ✅ Works in any environment

### 2. Reliability
- ✅ Validates hostname quality
- ✅ Never uses invalid values
- ✅ Always provides working URL

### 3. Predictability
- ✅ Clear priority order
- ✅ Explicit config option
- ✅ No surprises

### 4. Production Ready
- ✅ Container-friendly
- ✅ Cloud-native
- ✅ Easy to deploy

## API Reference

### get_server_hostname()

```python
from app.utils.hostname import get_server_hostname

# Basic usage
hostname = get_server_hostname()

# With fallback
hostname = get_server_hostname(fallback="backup.example.com")
```

### get_access_url()

```python
from app.utils.hostname import get_access_url

# Basic URL
url = get_access_url()
# http://example.com

# With path
url = get_access_url(path="/api")
# http://example.com/api

# With port
url = get_access_url(port=8888)
# http://example.com:8888

# HTTPS
url = get_access_url(protocol="https")
# https://example.com
```

## Migration Guide

### From Hardcoded "localhost"

**Before:**
```python
server_host = "localhost"
```

**After:**
```python
from app.utils.hostname import get_server_hostname
server_host = get_server_hostname()
```

### From Request Header Only

**Before:**
```python
server_host = request.headers.get("host", "localhost")
```

**After:**
```python
from app.utils.hostname import get_server_hostname
fallback = request.headers.get("host", "localhost")
server_host = get_server_hostname(fallback=fallback)
```

## Troubleshooting

### Issue: Wrong hostname displayed

**Solution:** Check priority chain:

```bash
# 1. Check config
grep HOSTNAME .env

# 2. Check system hostname
hostname

# 3. Check if system hostname is valid
# (not localhost, not IP, not empty)

# 4. Set explicit value
echo "HOSTNAME=your.domain.com" >> .env
./docklite restart
```

### Issue: URL shows IP address

**Problem:** System hostname is IP  
**Solution:** Set HOSTNAME in .env

```bash
echo "HOSTNAME=docklite.example.com" >> .env
./docklite restart
```

### Issue: URL shows "localhost" in production

**Problem:** No valid hostname found  
**Solutions:**

1. Set in config (recommended):
   ```bash
   echo "HOSTNAME=prod.example.com" >> .env
   ```

2. Or set system hostname:
   ```bash
   sudo hostnamectl set-hostname prod.example.com
   ```

## Summary

### Files Changed
- ✅ `backend/app/core/config.py` - Added HOSTNAME setting
- ✅ `backend/app/utils/hostname.py` - NEW utility (100+ lines)
- ✅ `backend/app/api/deployment.py` - Uses hostname utility
- ✅ `backend/tests/test_utils/test_hostname.py` - NEW tests (20+ tests)
- ✅ `README.md` - Updated with priority logic
- ✅ `HOSTNAME_SUPPORT.md` - Updated documentation
- ✅ `HOSTNAME_PRIORITY_LOGIC.md` - This document

### Tests Added
- ✅ 20+ new unit tests
- ✅ Priority logic coverage
- ✅ Validation logic coverage
- ✅ URL generation coverage
- ✅ Edge cases coverage

### Production Ready
- ✅ Tested and validated
- ✅ Multiple configuration options
- ✅ Automatic fallback chain
- ✅ Container-friendly
- ✅ Well documented

---

**Status:** ✅ Complete and Production Ready  
**Next:** Deploy and verify in production environment

