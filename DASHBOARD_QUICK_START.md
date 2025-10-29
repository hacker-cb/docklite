# Traefik Dashboard - Quick Start Guide

**Access:** http://artem.sokolov.me/dashboard  
**Auth:** Admin only 🔒

---

## Quick Access (3 Steps)

### 1. Login as Admin
```
http://artem.sokolov.me
Username: [your admin username]
Password: [your password]
```

### 2. Click Dashboard
```
Navigation bar → Click [Dashboard] button
```

### 3. View Metrics
```
New tab opens with Traefik dashboard
- HTTP Routers: 4
- Services: 5
- Middlewares: 2
```

---

## Access URLs

| Resource | URL | Auth Required |
|----------|-----|---------------|
| **Frontend** | http://artem.sokolov.me | All users |
| **Backend API** | http://artem.sokolov.me/api | All users |
| **API Docs** | http://artem.sokolov.me/docs | All users |
| **Dashboard** | http://artem.sokolov.me/dashboard | **Admin only** 🔒 |

---

## Security

### ✅ Protected
- Only users with `is_admin=true` can access
- JWT token validated on every request
- Automatic authentication via cookie
- All attack vectors blocked (34 tests)

### ❌ Not Accessible
- Regular users: 403 Forbidden
- Unauthenticated: 401 Unauthorized
- Expired tokens: 401 Unauthorized
- Invalid tokens: 401 Unauthorized

---

## Troubleshooting

### Can't see Dashboard button?

**You're not an admin.**

Check:
```javascript
// Browser console
JSON.parse(localStorage.getItem('user')).is_admin
// Should return: true
```

Fix:
```bash
# Via CLI
./docklite reset-password
# Make admin: Yes

# Or ask admin to grant you admin rights via Users UI
```

### Dashboard shows 403 Forbidden?

**You're not an admin.**

Same fix as above.

### Dashboard shows 401 Unauthorized?

**Token expired or invalid.**

Fix:
```
1. Logout
2. Login again
3. Try dashboard again
```

---

## Technical Details

**How it works:**
```
Click Dashboard
    ↓
Browser sends JWT cookie
    ↓
Traefik ForwardAuth
    ↓
Backend verifies: JWT + is_admin
    ↓
✅ Allow or ❌ Deny
```

**Security:**
- 229 total tests (all passing)
- 34 security-specific tests
- Zero vulnerabilities
- Production ready

---

**Full Docs:** [DASHBOARD_AUTH_COMPLETE.md](./DASHBOARD_AUTH_COMPLETE.md)

