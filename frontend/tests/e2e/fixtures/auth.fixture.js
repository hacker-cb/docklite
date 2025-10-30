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
  await page.goto('/');
  
  // Wait for login form
  await page.waitForSelector('input[type="text"]');
  
  // Fill credentials
  await page.fill('input[type="text"]', username);
  await page.fill('input[type="password"]', password);
  
  // Submit
  await page.click('button[type="submit"]');
  
  // Wait for navigation to complete
  await page.waitForURL('/');
  
  // Wait for app to load (check for navigation)
  await page.waitForSelector('nav', { timeout: 5000 });
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
    const context = await browser.newContext();
    const page = await context.newPage();
    
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    await use(page);
    
    await context.close();
  },
  
  /**
   * Regular user context
   */
  userPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    await login(page, TEST_USERS.user.username, TEST_USERS.user.password);
    
    await use(page);
    
    await context.close();
  },
});

export { expect } from '@playwright/test';

