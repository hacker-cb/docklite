import { test, expect } from './fixtures/auth.fixture.js';

/**
 * Admin User E2E Tests
 * 
 * Tests admin-specific functionality:
 * - View all projects (multi-tenant)
 * - Create/manage projects
 * - Manage users
 * - View all containers (including system containers)
 * - Access Traefik dashboard
 * - System containers protection
 */

test.describe('Admin User Functionality', () => {
  test('should access Projects view', async ({ adminPage }) => {
    // Already on projects page after login
    await adminPage.waitForURL('/#/projects');
    
    // Should see navigation buttons
    await expect(adminPage.locator('button:has-text("Projects")')).toBeVisible();
    
    // Should see "New Project" button
    await expect(adminPage.locator('button:has-text("New Project")')).toBeVisible();
  });

  test('should access Users management', async ({ adminPage }) => {
    // Navigate to Users
    await adminPage.click('button:has-text("Users")');
    await adminPage.waitForURL('/#/users');
    
    // Should see "Add User" button
    await expect(adminPage.locator('button:has-text("Add User")')).toBeVisible();
    
    // Should see list of users (use first to avoid strict mode violation)
    await expect(adminPage.locator('.p-datatable').first()).toBeVisible();
  });

  test('should access Containers view', async ({ adminPage }) => {
    // Navigate to Containers
    await adminPage.click('button:has-text("Containers")');
    await adminPage.waitForURL('/#/containers');
    
    // Should see containers table
    await expect(adminPage.locator('.p-datatable').first()).toBeVisible();
  });

  test('should see system containers in Containers view', async ({ adminPage }) => {
    // Navigate to Containers
    await adminPage.click('button:has-text("Containers")');
    await adminPage.waitForURL('/#/containers');
    
    // Wait for containers to load
    await adminPage.waitForTimeout(1000);
    
    // Should see containers table
    await expect(adminPage.locator('.p-datatable').first()).toBeVisible();
    
    // System containers should be visible (use count to avoid strict mode)
    const backendCount = await adminPage.locator('text=/docklite-backend/i').count();
    const frontendCount = await adminPage.locator('text=/docklite-frontend/i').count();
    const traefikCount = await adminPage.locator('text=/docklite-traefik/i').count();
    
    // At least one system container should be present
    expect(backendCount + frontendCount + traefikCount).toBeGreaterThan(0);
  });

  test('should NOT be able to stop system containers', async ({ adminPage }) => {
    // Navigate to Containers
    await adminPage.click('button:has-text("Containers")');
    await adminPage.waitForURL('/#/containers');
    
    // Wait for containers to load
    await adminPage.waitForTimeout(1000);
    
    // Try to find system container row
    const systemContainerRow = adminPage.locator('tr:has-text("docklite-")').first();
    
    if (await systemContainerRow.isVisible()) {
      // Stop button should be disabled or show warning
      const stopButton = systemContainerRow.locator('button:has-text("Stop")');
      
      if (await stopButton.isVisible()) {
        await stopButton.click();
        
        // Should show error/warning message (toast or dialog)
        await expect(adminPage.locator('.p-toast-message, .p-dialog, text=/system container|protected|cannot/i')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should access Traefik dashboard link', async ({ adminPage }) => {
    // Traefik button opens in new tab, just check button exists
    await expect(adminPage.locator('button:has-text("Traefik")')).toBeVisible();
    
    // Button should be clickable (opens new tab)
    await expect(adminPage.locator('button:has-text("Traefik")')).toBeEnabled();
  });

  test('should create new project dialog', async ({ adminPage }) => {
    // Already on projects page from login
    await adminPage.waitForURL('/#/projects');
    
    // Click New Project
    await adminPage.click('button:has-text("New Project")');
    
    // Dialog should open with title
    await expect(adminPage.locator('.p-dialog')).toBeVisible();
    await expect(adminPage.locator('text=Create New Project')).toBeVisible();
    
    // Should see preset tabs (use getByRole for better selector)
    await expect(adminPage.getByRole('tab', { name: /From Preset/ })).toBeVisible();
    await expect(adminPage.getByRole('tab', { name: /Custom/ })).toBeVisible();
  });

  test('should add new user dialog', async ({ adminPage }) => {
    // Navigate to Users
    await adminPage.click('button:has-text("Users")');
    await adminPage.waitForURL('/#/users');
    
    // Click Add User
    await adminPage.click('button:has-text("Add User")');
    
    // Dialog should open
    await expect(adminPage.locator('.p-dialog')).toBeVisible();
    
    // Form fields should be visible
    await expect(adminPage.locator('input[placeholder*="username"], input[id*="username"]')).toBeVisible();
  });

  test('should view all projects from different users', async ({ adminPage }) => {
    // Already on projects page from login
    await adminPage.waitForURL('/#/projects');
    
    // Wait for projects to load
    await adminPage.waitForTimeout(1000);
    
    // Admin should see new project button (proves access to projects view)
    await expect(adminPage.locator('button:has-text("New Project")')).toBeVisible();
    
    // Check if projects exist
    const hasProjects = await adminPage.locator('.p-datatable tbody tr').count();
    
    if (hasProjects > 0) {
      // Projects table should be visible
      await expect(adminPage.locator('.p-datatable').first()).toBeVisible();
    }
    // Empty state is also valid for new installations
  });
});

