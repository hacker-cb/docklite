import { test as base } from '@playwright/test';

/**
 * Authentication fixture for E2E tests
 * Provides authenticated contexts for admin and non-admin users
 */

/**
 * Test users credentials
 * These users should exist in the test database
 */
export const TEST_USERS = {
  admin: {
    username: 'cursor',
    password: 'CursorAI_Test2024!',
  },
  user: {
    username: 'testuser',
    password: 'TestUser_2024!',
  },
};

/**
 * Login helper function
 */
export async function login(page, username, password) {
  // Go to login page
  await page.goto('/login');
  
  // Wait for login form
  await page.waitForSelector('input#username', { state: 'visible' });
  
  // Fill credentials
  await page.fill('input#username', username);
  await page.fill('input#password', password);
  
  // Submit
  await page.click('button[type="submit"]');
  
  // Wait for successful login and redirect to projects
  await page.waitForURL('**/projects', { timeout: 10000 });
  
  // Wait for app to fully load
  await page.waitForSelector('button:has-text("Projects")', { state: 'visible', timeout: 5000 });
  
  // Additional wait for any async operations
  await page.waitForLoadState('networkidle');
}

/**
 * Logout helper function
 */
export async function logout(page) {
  await page.click('button:has-text("Logout")');
  await page.waitForURL('/login');
}

/**
 * Extended test with authenticated contexts
 */
export const test = base.extend({
  /**
   * Admin user context
   */
  adminPage: async ({ browser }, use) => {
    // Create fresh context with no storage
    const context = await browser.newContext({
      storageState: undefined,
    });
    const page = await context.newPage();
    
    // Login as admin
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    // Pass page to test
    await use(page);
    
    // Cleanup
    await context.close();
  },
  
  /**
   * Regular user context
   */
  userPage: async ({ browser }, use) => {
    // Create fresh context with no storage
    const context = await browser.newContext({
      storageState: undefined,
    });
    const page = await context.newPage();
    
    // Login as regular user
    await login(page, TEST_USERS.user.username, TEST_USERS.user.password);
    
    // Pass page to test
    await use(page);
    
    // Cleanup
    await context.close();
  },
});

export { expect } from '@playwright/test';

