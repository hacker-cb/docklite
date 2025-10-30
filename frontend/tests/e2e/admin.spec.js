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
    await adminPage.goto('/');
    
    // Navigate to Projects
    await adminPage.click('text=Projects');
    
    // Projects view should be visible
    await expect(adminPage.locator('h1')).toContainText('Projects');
    
    // Should see "Create Project" button
    await expect(adminPage.locator('button:has-text("Create Project")')).toBeVisible();
  });

  test('should access Users management', async ({ adminPage }) => {
    await adminPage.goto('/');
    
    // Navigate to Users
    await adminPage.click('text=Users');
    
    // Users view should be visible
    await expect(adminPage.locator('h1')).toContainText('Users');
    
    // Should see "Add User" button
    await expect(adminPage.locator('button:has-text("Add User")')).toBeVisible();
    
    // Should see list of users
    await expect(adminPage.locator('table')).toBeVisible();
  });

  test('should access Containers view', async ({ adminPage }) => {
    await adminPage.goto('/');
    
    // Navigate to Containers
    await adminPage.click('text=Containers');
    
    // Containers view should be visible
    await expect(adminPage.locator('h1')).toContainText('Containers');
    
    // Should see containers list
    await expect(adminPage.locator('table')).toBeVisible();
  });

  test('should see system containers in Containers view', async ({ adminPage }) => {
    await adminPage.goto('/containers');
    
    // Wait for containers to load
    await adminPage.waitForSelector('table tbody tr', { timeout: 10000 });
    
    // System containers should be visible
    const containers = await adminPage.locator('table tbody tr').count();
    expect(containers).toBeGreaterThan(0);
    
    // Should see system containers (docklite-backend, docklite-frontend, docklite-traefik)
    const backendVisible = await adminPage.locator('text=/docklite-backend/i').isVisible();
    const frontendVisible = await adminPage.locator('text=/docklite-frontend/i').isVisible();
    const traefikVisible = await adminPage.locator('text=/docklite-traefik/i').isVisible();
    
    // At least one system container should be visible
    expect(backendVisible || frontendVisible || traefikVisible).toBeTruthy();
  });

  test('should NOT be able to stop system containers', async ({ adminPage }) => {
    await adminPage.goto('/containers');
    
    // Wait for containers to load
    await adminPage.waitForSelector('table tbody tr', { timeout: 10000 });
    
    // Try to find system container row
    const systemContainerRow = adminPage.locator('tr:has-text("docklite-")').first();
    
    if (await systemContainerRow.isVisible()) {
      // Stop button should be disabled or show warning
      const stopButton = systemContainerRow.locator('button:has-text("Stop")');
      
      if (await stopButton.isVisible()) {
        await stopButton.click();
        
        // Should show error/warning message
        await expect(adminPage.locator('text=/system container|protected|cannot stop/i')).toBeVisible({ timeout: 3000 });
      }
    }
  });

  test('should access Traefik dashboard link', async ({ adminPage }) => {
    await adminPage.goto('/');
    
    // Navigate to Traefik
    await adminPage.click('text=Traefik');
    
    // Traefik view should be visible
    await expect(adminPage.locator('h1')).toContainText('Traefik');
    
    // Should see "Open Dashboard" button
    await expect(adminPage.locator('button:has-text("Open Dashboard")')).toBeVisible();
  });

  test('should create new project dialog', async ({ adminPage }) => {
    await adminPage.goto('/projects');
    
    // Click Create Project
    await adminPage.click('button:has-text("Create Project")');
    
    // Dialog should open
    await expect(adminPage.locator('role=dialog')).toBeVisible();
    
    // Form fields should be visible
    await expect(adminPage.locator('input[placeholder*="domain"]')).toBeVisible();
    await expect(adminPage.locator('select, .p-dropdown')).toBeVisible(); // Preset selector
  });

  test('should add new user dialog', async ({ adminPage }) => {
    await adminPage.goto('/users');
    
    // Click Add User
    await adminPage.click('button:has-text("Add User")');
    
    // Dialog should open
    await expect(adminPage.locator('role=dialog')).toBeVisible();
    
    // Form fields should be visible
    await expect(adminPage.locator('input[placeholder*="username"]')).toBeVisible();
    await expect(adminPage.locator('input[type="password"]')).toBeVisible();
  });

  test('should view all projects from different users', async ({ adminPage }) => {
    await adminPage.goto('/projects');
    
    // Wait for projects to load
    await adminPage.waitForTimeout(1000);
    
    // Admin should see projects counter or empty state
    const hasProjects = await adminPage.locator('table tbody tr').count();
    
    if (hasProjects > 0) {
      // Projects table should be visible
      await expect(adminPage.locator('table')).toBeVisible();
    } else {
      // Empty state should be visible
      await expect(adminPage.locator('text=/no projects|empty/i')).toBeVisible();
    }
  });
});

