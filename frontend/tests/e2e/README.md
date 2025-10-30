# DockLite E2E Tests

End-to-end tests for DockLite UI using Playwright.

## Overview

E2E tests validate the entire user flow through a real browser, testing:
- Authentication and authorization
- Admin vs non-admin user experiences
- Multi-tenancy isolation
- UI interactions
- API integration

## Test Structure

```
tests/e2e/
├── fixtures/
│   └── auth.fixture.js       # Authentication helpers and test users
├── auth.spec.js              # Login/logout tests
├── admin.spec.js             # Admin user functionality
├── user.spec.js              # Non-admin user functionality
└── README.md                 # This file
```

## Test Users

Tests use predefined test users:

**Admin user:**
- Username: `cursor`
- Password: `CursorAI_Test2024!`

**Regular user:**
- Username: `testuser`
- Password: `TestUser_2024!`

**Create test users before running tests:**
```bash
# Create admin user (already exists)
./docklite add-user cursor -p "CursorAI_Test2024!" --admin

# Create regular user
./docklite add-user testuser -p "TestUser_2024!" --user
```

## Running Tests

### Prerequisites

1. Install Playwright:
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

2. Start DockLite:
```bash
./docklite start
```

3. Create test users (see above)

### Run All E2E Tests

```bash
cd frontend
npm run test:e2e
```

### Run Specific Test File

```bash
npx playwright test auth.spec.js
npx playwright test admin.spec.js
npx playwright test user.spec.js
```

### Run in UI Mode (Interactive)

```bash
npm run test:e2e:ui
```

### Run in Debug Mode

```bash
npx playwright test --debug
```

### View Test Report

```bash
npx playwright show-report
```

## Test Coverage

### Authentication Tests (`auth.spec.js`)
- ✅ Show login form for unauthenticated user
- ✅ Login with admin credentials
- ✅ Login with user credentials
- ✅ Show error for invalid credentials
- ✅ Logout successfully
- ✅ Maintain session after reload
- ✅ Redirect to login for protected routes

### Admin Tests (`admin.spec.js`)
- ✅ Access Projects view
- ✅ Access Users management
- ✅ Access Containers view
- ✅ See system containers
- ✅ System containers protection (cannot stop)
- ✅ Access Traefik dashboard link
- ✅ Create new project dialog
- ✅ Add new user dialog
- ✅ View all projects (multi-tenant)

### Non-Admin Tests (`user.spec.js`)
- ✅ Limited navigation menu
- ✅ Access Projects view
- ✅ See only own projects (multi-tenancy)
- ✅ Access Containers view
- ✅ NOT see system containers
- ✅ NOT access Users page
- ✅ NOT access Traefik page
- ✅ Create project dialog
- ✅ See own containers only

## CI/CD Integration

Add to `.github/workflows/test-e2e.yml`:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
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
          # Wait for services
          sleep 10
      
      - name: Create test users
        run: |
          ./docklite add-user cursor -p "CursorAI_Test2024!" --admin
          ./docklite add-user testuser -p "TestUser_2024!" --user
      
      - name: Run E2E tests
        run: cd frontend && npm run test:e2e
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Writing New Tests

### Use Authentication Fixtures

```javascript
import { test, expect } from './fixtures/auth.fixture.js';

test('my admin test', async ({ adminPage }) => {
  // adminPage is already authenticated as admin
  await adminPage.goto('/some-page');
  // ... test code
});

test('my user test', async ({ userPage }) => {
  // userPage is already authenticated as regular user
  await userPage.goto('/some-page');
  // ... test code
});
```

### Test Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Wait for elements** before interacting
3. **Test user perspective**, not implementation
4. **Keep tests independent** (no shared state)
5. **Use descriptive test names**
6. **Test both happy and error paths**

## Troubleshooting

### Tests fail with "Element not found"
- Increase timeout: `await page.waitForSelector('element', { timeout: 10000 })`
- Check if element selector is correct
- Use `--debug` flag to see what's happening

### Tests fail with "Connection refused"
- Make sure DockLite is running: `./docklite status`
- Check correct port in `playwright.config.js`

### Authentication fails
- Verify test users exist: `./docklite list-users`
- Check credentials in `auth.fixture.js`

### Flaky tests
- Add explicit waits: `await page.waitForLoadState('networkidle')`
- Use `{ timeout: 10000 }` for slow operations
- Run tests in series: `npx playwright test --workers=1`

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Tests](https://playwright.dev/docs/debug)

