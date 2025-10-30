# E2E Testing Guide

End-to-end testing documentation for DockLite using Playwright.

## Quick Start

```bash
# 1. Install Playwright
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium

# 2. Create test users
./docklite add-user cursor -p "CursorAI_Test2024!" --admin
./docklite add-user testuser -p "TestUser_2024!" --user

# 3. Start DockLite
./docklite start

# 4. Run E2E tests
./docklite test-e2e
```

## Commands

### Run All E2E Tests
```bash
./docklite test-e2e
```

Runs all 24 E2E tests in headless mode.

### Interactive Mode
```bash
./docklite test-e2e --ui
```

Opens Playwright UI for interactive test exploration and debugging.

### Debug Mode
```bash
./docklite test-e2e --debug
```

Runs tests in debug mode with step-through capabilities.

### Show Browser
```bash
./docklite test-e2e --headed
```

Runs tests with visible browser window.

### View Report
```bash
./docklite test-e2e --report
```

Opens the test report in browser.

## Test Coverage

**Total: 24 tests**

### Authentication (7 tests)
- Login form display
- Admin login
- User login
- Invalid credentials
- Logout
- Session persistence
- Protected routes

### Admin User (9 tests)
- Access Projects view
- Access Users management
- Access Containers view
- See system containers
- System containers protection (cannot stop)
- Traefik dashboard access
- Create project dialog
- Add user dialog
- View all projects (multi-tenant)

### Non-Admin User (8 tests)
- Limited navigation menu
- Access Projects view
- See only own projects (multi-tenancy)
- Access Containers view
- NOT see system containers
- NOT access Users page
- NOT access Traefik page
- See own containers only

## Test Users

E2E tests require two test users:

**Admin:**
- Username: `cursor`
- Password: `CursorAI_Test2024!`
- Role: Admin

**Regular User:**
- Username: `testuser`
- Password: `TestUser_2024!`
- Role: User

Create them with:
```bash
./docklite add-user cursor -p "CursorAI_Test2024!" --admin
./docklite add-user testuser -p "TestUser_2024!" --user
```

## File Structure

```
frontend/tests/e2e/
├── fixtures/
│   └── auth.fixture.js       # Authentication helpers
├── auth.spec.js              # Authentication tests (7)
├── admin.spec.js             # Admin user tests (9)
├── user.spec.js              # Non-admin user tests (8)
└── README.md                 # Detailed E2E documentation
```

## Configuration

**File:** `frontend/playwright.config.js`

Key settings:
- **Base URL:** `http://localhost` (auto-detected from env)
- **Timeout:** 30 seconds per test
- **Retries:** 0 (local), 2 (CI)
- **Screenshot:** On failure
- **Video:** Retain on failure
- **Browser:** Chromium

## Writing E2E Tests

### Use Authentication Fixtures

```javascript
import { test, expect } from './fixtures/auth.fixture.js';

test('my admin test', async ({ adminPage }) => {
  // adminPage is already authenticated as admin
  await adminPage.goto('/projects');
  // ... test code
});

test('my user test', async ({ userPage }) => {
  // userPage is already authenticated as regular user
  await userPage.goto('/projects');
  // ... test code
});
```

### Test Best Practices

1. **Use data-testid** for stable selectors
2. **Wait for elements** before interacting
3. **Test user perspective**, not implementation
4. **Keep tests independent** (no shared state)
5. **Use descriptive names**
6. **Test happy and error paths**

## Troubleshooting

### Playwright Not Installed

**Error:** `Playwright is not installed!`

**Solution:**
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

### Test Users Missing

**Error:** Tests fail with authentication errors

**Solution:**
```bash
./docklite add-user cursor -p "CursorAI_Test2024!" --admin
./docklite add-user testuser -p "TestUser_2024!" --user
```

### DockLite Not Running

**Error:** `Connection refused` or timeout errors

**Solution:**
```bash
./docklite start
./docklite status  # Verify services are running
```

### Tests Flaky

**Solution:**
- Add explicit waits: `await page.waitForLoadState('networkidle')`
- Increase timeouts for slow operations
- Run tests in series: `--workers=1`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Install Playwright
        run: cd frontend && npx playwright install --with-deps chromium
      
      - name: Start DockLite
        run: |
          ./docklite setup-dev
          ./docklite start
      
      - name: Create test users
        run: |
          ./docklite add-user cursor -p "CursorAI_Test2024!" --admin
          ./docklite add-user testuser -p "TestUser_2024!" --user
      
      - name: Run E2E tests
        run: ./docklite test-e2e
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Performance

**Typical run time:**
- All 24 tests: ~45 seconds
- Single test file: ~15 seconds
- With --ui mode: Interactive (unlimited)

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [DockLite E2E README](frontend/tests/e2e/README.md)
- [HOW_TO_RUN_TESTS.md](HOW_TO_RUN_TESTS.md)

## Summary

✅ **24 E2E tests** covering authentication, authorization, and user flows  
✅ **Admin and non-admin** scenarios tested  
✅ **Multi-tenancy** isolation verified  
✅ **System protection** validated  
✅ **Interactive debugging** available with `--ui` flag  
✅ **CI/CD ready** for automated testing

