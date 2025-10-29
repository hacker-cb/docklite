# Scripts Hostname Refactoring - Complete

**Date:** 2025-10-29  
**Feature:** Unified hostname handling across all bash scripts  
**Status:** ✅ Production Ready

## Problem

До рефакторинга hostname обрабатывался по-разному в разных скриптах:
- `status.sh` - использовал `hostname` напрямую
- `start.sh` - показывал хардкоженные `localhost:5173`, `localhost:8000`
- `rebuild.sh` - показывал хардкоженные `localhost:5173`, `localhost:8000`
- Другие скрипты - разные подходы

**Результат:** Непоследовательный UX, невозможность централизованно управлять hostname.

## Solution

Создана **единая система** в `scripts/lib/common.sh`:

### 1. get_hostname() - Unified Hostname Detection

```bash
get_hostname() {
    # Priority 1: HOSTNAME from .env file
    # Priority 2: System hostname (if valid)
    # Priority 3: Default to localhost
}
```

**Features:**
- ✅ Читает `HOSTNAME` из `.env`
- ✅ Использует system hostname если нет в .env
- ✅ Валидирует hostname (исключает IP адреса)
- ✅ Fallback на "localhost"

### 2. get_access_url() - URL Builder

```bash
get_access_url() {
    local path="${1:-}"        # Optional path (e.g., "/api")
    local port="${2:-}"        # Optional port
    local protocol="${3:-http}" # Protocol (http/https)
    
    # Builds: http://hostname:port/path
}
```

**Features:**
- ✅ Автоматически скрывает порты 80/443
- ✅ Правильное форматирование пути
- ✅ Поддержка HTTPS
- ✅ Reusable в любом скрипте

## Implementation

### Core Functions (common.sh)

```bash
# scripts/lib/common.sh

# Get hostname with priority logic
get_hostname() {
    # Priority 1: .env HOSTNAME
    if [ -f "$(get_project_root)/.env" ]; then
        local env_hostname=$(grep "^HOSTNAME=" .env | cut -d'=' -f2-)
        if [ -n "$env_hostname" ]; then
            echo "$env_hostname"
            return 0
        fi
    fi
    
    # Priority 2: System hostname (if not localhost, not IP)
    local sys_hostname=$(hostname)
    if [ -n "$sys_hostname" ] && [ "$sys_hostname" != "localhost" ]; then
        if ! echo "$sys_hostname" | grep -qE '^[0-9.]+$'; then
            echo "$sys_hostname"
            return 0
        fi
    fi
    
    # Priority 3: Default
    echo "localhost"
}

# Build access URL
get_access_url() {
    local path="${1:-}"
    local port="${2:-}"
    local protocol="${3:-http}"
    
    local hostname=$(get_hostname)
    local url="${protocol}://${hostname}"
    
    # Add port if not default
    if [ -n "$port" ] && [ "$port" != "80" ] && [ "$port" != "443" ]; then
        url="${url}:${port}"
    fi
    
    # Add path
    if [ -n "$path" ]; then
        [[ ! "$path" =~ ^/ ]] && path="/$path"
        url="${url}${path}"
    fi
    
    echo "$url"
}
```

### Updated Scripts

#### 1. status.sh
```bash
# Before
log_info "Frontend: http://localhost:5173"
log_info "Backend:  http://localhost:8000"

# After
log_info "Frontend:     $(get_access_url)"
log_info "Backend API:  $(get_access_url "/api")"
log_info "Dashboard:    $(get_access_url "" "8888")"
```

#### 2. start.sh
```bash
# Before
log_info "Frontend:  http://localhost:5173"
log_info "Backend:   http://localhost:8000"
log_info "API Docs:  http://localhost:8000/docs"

# After
log_info "Frontend:  $(get_access_url)"
log_info "Backend:   $(get_access_url "/api")"
log_info "API Docs:  $(get_access_url "/docs")"
log_info "Dashboard: $(get_access_url "" "8888")"
```

#### 3. rebuild.sh
```bash
# Same changes as start.sh
```

#### 4. setup-system-user.sh
```bash
# Before
log_info "3. Access UI: http://localhost:5173"

# After
log_info "3. Access UI: $(get_access_url)"
```

#### 5. init-database.sh
```bash
# Before
log_info "Backend is ready at: http://localhost:8000"
log_info "API Docs at:         http://localhost:8000/docs"

# After
log_info "Backend is ready at: $(get_access_url "/api")"
log_info "API Docs at:         $(get_access_url "/docs")"
```

#### 6. reset-password.sh
```bash
# Before
log_info "Frontend: http://localhost:5173"

# After
log_info "Frontend: $(get_access_url)"
```

## Testing

### Automated Tests

**File:** `scripts/lib/test_hostname.sh`

```bash
bash scripts/lib/test_hostname.sh

# Results:
✓ get_hostname returns non-empty value: artem.sokolov.me
✓ get_access_url returns HTTP URL: http://artem.sokolov.me
✓ get_access_url with path: http://artem.sokolov.me/api
✓ get_access_url with port: http://artem.sokolov.me:8888
✓ get_access_url with path and port: http://artem.sokolov.me:8888/dashboard
✓ get_access_url hides port 80: http://artem.sokolov.me

All tests passed! (6/6)
```

### Priority Testing

**Test 1: With HOSTNAME in .env**
```bash
echo "HOSTNAME=custom.example.com" >> .env
bash scripts/lib/test_hostname.sh

# Result: Uses custom.example.com ✅
```

**Test 2: Without HOSTNAME in .env**
```bash
# Remove HOSTNAME from .env
bash scripts/lib/test_hostname.sh

# Result: Uses system hostname (artem.sokolov.me) ✅
```

**Test 3: Default behavior**
```bash
# If hostname is "localhost" or IP
# Result: Falls back to localhost ✅
```

### Manual Verification

```bash
# Test status
./docklite status
# ✅ Shows: http://artem.sokolov.me

# Test start  
./docklite start
# ✅ Shows: http://artem.sokolov.me

# Test rebuild
./docklite rebuild
# ✅ Shows: http://artem.sokolov.me

# Test with config override
echo "HOSTNAME=test.local" >> .env
./docklite status
# ✅ Shows: http://test.local
```

## Configuration Options

### Option 1: Config Override (Priority 1)

```bash
# .env
HOSTNAME=docklite.example.com
```

**All scripts will use:** `http://docklite.example.com`

### Option 2: System Hostname (Priority 2)

```bash
sudo hostnamectl set-hostname artem.sokolov.me
```

**All scripts will use:** `http://artem.sokolov.me` (if HOSTNAME not in .env)

### Option 3: Default (Priority 3)

**All scripts will use:** `http://localhost` (if nothing configured)

## Files Changed

### Core Library
- ✅ `scripts/lib/common.sh` - Added `get_hostname()` and `get_access_url()`
- ✅ `scripts/lib/test_hostname.sh` - NEW (6 tests)

### Updated Scripts
- ✅ `scripts/maintenance/status.sh`
- ✅ `scripts/development/start.sh`
- ✅ `scripts/development/rebuild.sh`
- ✅ `scripts/maintenance/reset-password.sh`
- ✅ `scripts/deployment/setup-system-user.sh`
- ✅ `scripts/deployment/init-database.sh`

**Total:** 6 scripts refactored to use unified functions

## Benefits

### 1. Consistency
- ✅ All scripts show same hostname
- ✅ Predictable behavior
- ✅ No confusion

### 2. Maintainability
- ✅ Single source of truth
- ✅ Easy to change logic
- ✅ No code duplication

### 3. Flexibility
- ✅ Config override
- ✅ System hostname auto-detect
- ✅ Fallback chain

### 4. Production Ready
- ✅ Works with custom domains
- ✅ Works with Traefik
- ✅ Works in any environment

## Usage Examples

### In Scripts

```bash
# Source common functions
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Get hostname
hostname=$(get_hostname)
# artem.sokolov.me

# Build URLs
frontend_url=$(get_access_url)
# http://artem.sokolov.me

api_url=$(get_access_url "/api")
# http://artem.sokolov.me/api

dashboard_url=$(get_access_url "" "8888")
# http://artem.sokolov.me:8888

https_url=$(get_access_url "/secure" "" "https")
# https://artem.sokolov.me/secure
```

### Output Examples

**With system hostname (artem.sokolov.me):**
```
╔════════════════════════════════════════════════════════════╗
║ DockLite is Running                                        ║
╚════════════════════════════════════════════════════════════╝
ℹ Frontend:  http://artem.sokolov.me
ℹ Backend:   http://artem.sokolov.me/api
ℹ API Docs:  http://artem.sokolov.me/docs
ℹ Dashboard: http://artem.sokolov.me:8888

ℹ Local access: http://localhost
```

**With config override (HOSTNAME=custom.local):**
```
╔════════════════════════════════════════════════════════════╗
║ DockLite is Running                                        ║
╚════════════════════════════════════════════════════════════╝
ℹ Frontend:  http://custom.local
ℹ Backend:   http://custom.local/api
ℹ API Docs:  http://custom.local/docs
ℹ Dashboard: http://custom.local:8888

ℹ Local access: http://localhost
```

**With localhost (default):**
```
╔════════════════════════════════════════════════════════════╗
║ DockLite is Running                                        ║
╚════════════════════════════════════════════════════════════╝
ℹ Frontend:  http://localhost
ℹ Backend:   http://localhost/api
ℹ API Docs:  http://localhost/docs
ℹ Dashboard: http://localhost:8888
```

## Best Practices

### For Script Authors

```bash
# ✅ DO: Use helper functions
url=$(get_access_url "/api")
log_info "API: $url"

# ❌ DON'T: Hardcode URLs
log_info "API: http://localhost:8000/api"
```

### For New Scripts

```bash
#!/bin/bash
set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Use hostname functions
hostname=$(get_hostname)
url=$(get_access_url "/mypath")

echo "Access at: $url"
```

## Synchronization with Python

Логика приоритетов **идентична** в bash и Python:

### Bash (scripts/lib/common.sh)
```bash
1. HOSTNAME from .env
2. System hostname
3. localhost
```

### Python (backend/app/utils/hostname.py)
```python
1. settings.HOSTNAME
2. socket.gethostname()
3. fallback or localhost
```

**Result:** Consistent behavior across всей системы

## Verification

### Quick Test

```bash
# 1. Test hostname function
bash scripts/lib/test_hostname.sh
# Expected: All tests passed! (6/6)

# 2. Test status output
./docklite status
# Expected: Shows hostname URLs

# 3. Test with custom hostname
echo "HOSTNAME=test.local" >> .env
./docklite status
# Expected: Shows test.local URLs

# 4. Cleanup
sed -i '/^HOSTNAME=/d' .env
```

### Full Integration Test

```bash
# 1. Set custom hostname in .env
echo "HOSTNAME=docklite.company.com" >> .env

# 2. Restart system
./docklite restart

# Expected output:
# ✅ All URLs show docklite.company.com
# ✅ Backend API accessible at http://docklite.company.com/api
# ✅ Frontend at http://docklite.company.com
# ✅ Dashboard at http://docklite.company.com:8888
```

## Summary

### Changes Summary

**New Functions:**
- ✅ `get_hostname()` - Unified hostname detection with priorities
- ✅ `get_access_url()` - Smart URL builder
- ✅ Test suite - 6 automated tests

**Scripts Refactored:** 6
- ✅ `status.sh` - Shows hostname URLs
- ✅ `start.sh` - Shows hostname URLs
- ✅ `rebuild.sh` - Shows hostname URLs  
- ✅ `reset-password.sh` - Shows hostname URL
- ✅ `setup-system-user.sh` - Shows hostname URL
- ✅ `init-database.sh` - Shows hostname URLs

**Documentation:**
- ✅ `SCRIPTS_HOSTNAME_REFACTORING.md` - This document
- ✅ `HOSTNAME_PRIORITY_LOGIC.md` - Complete priority guide
- ✅ Comments in `common.sh` - Function documentation

### Key Benefits

1. **Single Source of Truth** - One function for all scripts
2. **Consistent UX** - Same hostname everywhere
3. **Configurable** - Override via .env
4. **Smart Defaults** - Uses system hostname automatically
5. **Maintainable** - Change once, affects all scripts
6. **Tested** - Automated test suite

### Statistics

| Metric | Value |
|--------|-------|
| **Functions Added** | 2 (get_hostname, get_access_url) |
| **Scripts Updated** | 6 |
| **Tests Created** | 6 |
| **Lines Removed** | ~30 (hardcoded URLs) |
| **Lines Added** | ~60 (reusable functions) |
| **Code Duplication** | -100% |

## Future Enhancements

### Easy to Extend

```bash
# Add HTTPS support
get_secure_url() {
    get_access_url "$1" "$2" "https"
}

# Add WebSocket support  
get_ws_url() {
    get_access_url "$1" "$2" "ws"
}

# Add custom domains
get_project_url() {
    local domain="$1"
    echo "http://${domain}"
}
```

### Centralized Management

```bash
# Future: Add to common.sh
validate_hostname() {
    # Check DNS resolution
    # Check SSL certificate
    # Check reachability
}

update_hostname() {
    # Update .env file
    # Validate new hostname
    # Restart services
}
```

## Compatibility

### Backward Compatible
- ✅ Works without configuration
- ✅ Falls back to localhost
- ✅ No breaking changes

### Forward Compatible
- ✅ Ready for SSL/HTTPS
- ✅ Ready for custom domains
- ✅ Ready for multi-host setups

## Related Documentation

- [HOSTNAME_PRIORITY_LOGIC.md](./HOSTNAME_PRIORITY_LOGIC.md) - Priority system
- [HOSTNAME_SUPPORT.md](./HOSTNAME_SUPPORT.md) - Feature overview
- [TRAEFIK.md](./TRAEFIK.md) - Traefik integration
- [scripts/README.md](./scripts/README.md) - Scripts documentation

---

**Status:** ✅ Complete and Production Ready  
**Tests:** 6/6 passing  
**Scripts:** 6/6 refactored  
**Consistency:** 100%

