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
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with admin credentials', async ({ page }) => {
    await login(page, TEST_USERS.admin.username, TEST_USERS.admin.password);
    
    // Should be on home page
    await expect(page).toHaveURL('/');
    
    // Navigation should be visible
    await expect(page.locator('nav')).toBeVisible();
    
    // Admin should see all menu items
    await expect(page.locator('text=Projects')).toBeVisible();
    await expect(page.locator('text=Users')).toBeVisible();
    await expect(page.locator('text=Containers')).toBeVisible();
    await expect(page.locator('text=Traefik')).toBeVisible();
  });

  test('should login successfully with user credentials', async ({ page }) => {
    await login(page, TEST_USERS.user.username, TEST_USERS.user.password);
    
    // Should be on home page
    await expect(page).toHaveURL('/');
    
    // Navigation should be visible
    await expect(page.locator('nav')).toBeVisible();
    
    // User should see limited menu items
    await expect(page.locator('text=Projects')).toBeVisible();
    await expect(page.locator('text=Containers')).toBeVisible();
    
    // User should NOT see admin-only items
    await expect(page.locator('text=Users')).not.toBeVisible();
    await expect(page.locator('text=Traefik')).not.toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/');
    
    await page.fill('input[type="text"]', 'invalid_user');
    await page.fill('input[type="password"]', 'wrong_password');
    await page.click('button[type="submit"]');
    
    // Should stay on login page
    await expect(page).toHaveURL(/login/);
    
    // Error message should be visible
    await expect(page.locator('text=/Invalid credentials|Authentication failed/i')).toBeVisible();
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
    
    // Should still be authenticated
    await expect(page).toHaveURL('/');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/projects');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/login/);
  });
});

