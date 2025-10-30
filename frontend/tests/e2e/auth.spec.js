import { test, expect } from '@playwright/test';
import { TEST_USERS, login, logout } from './fixtures/auth.fixture.js';

/**
 * Authentication E2E Tests
 * 
 * Tests:
 * - Login with valid credentials
 * - Login with invalid credentials
 * - Logout
 * - Session persistence
 * - Access without authentication
 */

test.describe('Authentication', () => {
  test('should show login form for unauthenticated user', async ({ page }) => {
    await page.goto('/');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/login/);
    
    // Login form should be visible
    await expect(page.locator('input#username')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with admin credentials', async ({ page }) => {
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    // Should be on projects page
    await expect(page).toHaveURL('/#/projects');
    
    // Navigation buttons should be visible
    await expect(page.locator('button:has-text("Projects")')).toBeVisible();
    
    // Admin should see all menu items
    await expect(page.locator('button:has-text("Projects")')).toBeVisible();
    await expect(page.locator('button:has-text("Users")')).toBeVisible();
    await expect(page.locator('button:has-text("Containers")')).toBeVisible();
    await expect(page.locator('button:has-text("Traefik")')).toBeVisible();
  });

  test('should login successfully with user credentials', async ({ page }) => {
    await login(page, TEST_USERS.user.username, TEST_USERS.user.password);
    
    // Should be on projects page
    await expect(page).toHaveURL('/#/projects');
    
    // Navigation buttons should be visible
    await expect(page.locator('button:has-text("Projects")')).toBeVisible();
    
    // User should NOT see admin-only items
    await expect(page.locator('button:has-text("Users")')).not.toBeVisible();
    await expect(page.locator('button:has-text("Containers")')).not.toBeVisible();
    await expect(page.locator('button:has-text("Traefik")')).not.toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/');
    
    // Wait for login form
    await page.waitForSelector('input#username');
    
    await page.fill('input#username', 'invalid_user');
    await page.fill('input#password', 'wrong_password');
    await page.click('button[type="submit"]');
    
    // Wait for login attempt to complete
    await page.waitForTimeout(2000);
    
    // Should stay on login page (login failed)
    await expect(page).toHaveURL(/login/);
    
    // Login form should still be visible (not redirected)
    await expect(page.locator('input#username')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    // Click logout
    await logout(page);
    
    // Should be redirected to login
    await expect(page).toHaveURL(/login/);
    
    // Trying to access home should redirect to login
    await page.goto('/');
    await expect(page).toHaveURL(/login/);
  });

  test('should maintain session after page reload', async ({ page }) => {
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    // Reload page
    await page.reload();
    
    // Should still be authenticated and on projects page
    await expect(page).toHaveURL('/#/projects');
    await expect(page.locator('button:has-text("Projects")')).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/projects');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/login/);
  });
});

