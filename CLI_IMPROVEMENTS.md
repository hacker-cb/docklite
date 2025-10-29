# CLI Improvements - User Management

**Date:** 2025-10-29  
**Feature:** Enhanced user management commands  
**Status:** ✅ Complete

---

## Overview

Улучшены CLI команды для управления пользователями с лучшим UX и error handling.

---

## New Command: list-users

### Usage

```bash
# Simple list
./docklite list-users

# Detailed info
./docklite list-users --verbose
```

### Output Examples

**Simple Mode:**
```
╔════════════════════════════════════════════════════════════╗
║ DockLite Users                                             ║
╚════════════════════════════════════════════════════════════╝

▶ Loading users...

✅ admin (admin)
ℹ  testuser (user)
ℹ  developer (user)

ℹ Total users: 3

ℹ Use --verbose for detailed information
```

**Verbose Mode:**
```
╔════════════════════════════════════════════════════════════╗
║ DockLite Users                                             ║
╚════════════════════════════════════════════════════════════╝

▶ Loading users...

ID    Username             Email                          Role       Status     System User
------------------------------------------------------------------------------------------
1     admin                admin@example.com              admin      active     docklite
2     testuser             test@example.com               user       active     docklite
3     developer            dev@example.com                user       active     docklite
4     inactive             old@example.com                user       inactive   docklite

ℹ Total users: 4
```

---

## Improved: reset-password

### Enhanced Features

**1. User Existence Check**
```bash
$ ./docklite reset-password nonexistent

❌ User 'nonexistent' not found!

▶ Existing users:
  ℹ admin (admin)
  ℹ testuser (user)
  ℹ developer (user)

ℹ Usage: ./docklite reset-password <username>
```

**2. Empty Database Check**
```bash
$ ./docklite reset-password admin

⚠️  No users found in database!
ℹ Use the setup screen to create the first admin user:
ℹ http://artem.sokolov.me
```

**3. Success with Instructions**
```bash
$ ./docklite reset-password admin

▶ Checking existing users...
ℹ Username: admin

▶ Enter new password for user 'admin':
Password: ********
Confirm password: ********

▶ Resetting password...
✅ Password reset successfully!

ℹ You can now login with:
  ℹ Username: admin
  ℹ Password: [your new password]

ℹ Frontend: http://artem.sokolov.me
```

---

## Implementation

### list-users.sh

**File:** `scripts/maintenance/list-users.sh`

**Features:**
- Lists all users from database
- Shows role (admin/user)
- Shows status (active/inactive)
- Verbose mode with full details
- Color-coded output
- Uses hostname functions

**Code:**
```bash
# Simple list
docker exec backend python -c "
  SELECT username, is_admin, is_active FROM users
  FORMAT: username:role:status
"

# Verbose list
docker exec backend python -c "
  SELECT id, username, email, is_admin, is_active, system_user
  FORMAT: table
"
```

### reset-password.sh Improvements

**Enhanced Checks:**
```bash
# 1. Get all users
USERS_LIST=$(docker exec backend list_users)

# 2. Check if NO_USERS
if [ "$USERS_LIST" = "NO_USERS" ]; then
    # Show setup instruction
fi

# 3. Check if user exists
if ! echo "$USERS_LIST" | grep -q "^${USERNAME}:"; then
    # Show existing users list
    # Show usage
    exit 1
fi

# 4. Proceed with password reset
```

---

## Usage Examples

### List All Users

```bash
# Quick list
./docklite list-users

# Detailed list with emails
./docklite list-users --verbose
```

### Reset Password

```bash
# Interactive (recommended)
./docklite reset-password admin

# With password argument (scripting)
./docklite reset-password admin --password NewSecurePass123
```

### Common Workflows

**Workflow 1: Find username**
```bash
./docklite list-users
# See list of users
# Pick username

./docklite reset-password <username>
```

**Workflow 2: Check user role**
```bash
./docklite list-users --verbose
# See full user details including role
```

**Workflow 3: Grant admin rights**
```bash
# Currently requires UI or database edit
# Future: ./docklite grant-admin <username>
```

---

## Error Handling

### No Users in Database

```bash
$ ./docklite list-users

⚠️  No users found in database!
ℹ Use the setup screen to create the first admin user:
ℹ http://artem.sokolov.me
```

### User Not Found

```bash
$ ./docklite reset-password unknown

❌ User 'unknown' not found!

▶ Existing users:
  ℹ admin (admin)
  ℹ testuser (user)
```

### Backend Not Running

```bash
$ ./docklite list-users

⚠️  Backend is not running. Starting it...
[Starting backend...]
✅ Backend started

[Lists users]
```

---

## Files Changed

### New Files (1)
1. ✅ `scripts/maintenance/list-users.sh` - NEW (100+ lines)

### Modified Files (2)
1. ✅ `scripts/maintenance/reset-password.sh` - Enhanced with user check
2. ✅ `scripts/docklite.sh` - Added list-users command

---

## Integration with Completion

Update bash completion to include new command:

```bash
# scripts/completion/docklite-completion.bash
commands="start stop restart ... list-users reset-password ..."
```

---

## Benefits

### For Users

✅ **See who exists** before resetting password  
✅ **Clear error messages** when user not found  
✅ **Helpful suggestions** with existing users  
✅ **No guessing** - see all available users  

### For Admins

✅ **Quick overview** of all users  
✅ **Check roles** easily  
✅ **See inactive users** at a glance  
✅ **Detailed info** with --verbose  

### For Operations

✅ **Better UX** - Less frustration  
✅ **Self-service** - Users can check themselves  
✅ **Audit** - See all users quickly  
✅ **Troubleshooting** - Verify user exists  

---

## Future Enhancements

### Planned Commands

```bash
# Create user via CLI
./docklite create-user <username> [--admin]

# Grant/revoke admin
./docklite grant-admin <username>
./docklite revoke-admin <username>

# Activate/deactivate
./docklite activate-user <username>
./docklite deactivate-user <username>

# Delete user
./docklite delete-user <username>
```

### Enhanced list-users

```bash
# Filter by role
./docklite list-users --admins-only
./docklite list-users --users-only

# Filter by status
./docklite list-users --active
./docklite list-users --inactive

# Search
./docklite list-users --search pavel

# Export
./docklite list-users --json > users.json
./docklite list-users --csv > users.csv
```

---

## Testing

### Manual Tests

```bash
# Test 1: List users (when Docker running)
./docklite list-users
# Expected: Shows user list ✅

# Test 2: Verbose mode
./docklite list-users --verbose
# Expected: Shows detailed table ✅

# Test 3: Reset existing user
./docklite list-users
# Copy username
./docklite reset-password <username>
# Expected: Works ✅

# Test 4: Reset non-existent user
./docklite reset-password fakename
# Expected: Shows error + user list ✅
```

---

## Documentation

### Help Text

```bash
# List users help
./docklite list-users --help

# Reset password help
./docklite reset-password --help

# Main help
./docklite --help
```

### Man Page Ready

Commands are documented with:
- Usage examples
- Options
- Error messages
- Related commands

---

## Summary

**CLI User Management Enhanced!**

- ✅ **New Command:** `list-users` for viewing all users
- ✅ **Improved:** `reset-password` with user validation
- ✅ **Better UX:** Clear errors, helpful suggestions
- ✅ **Professional:** Color-coded, well-formatted output
- ✅ **Integrated:** Works with hostname system

**Status:** ✅ Production Ready

---

**Usage:**

```bash
# See all users
./docklite list-users

# Reset password for existing user
./docklite reset-password admin
```

Simple and effective! 🎯

