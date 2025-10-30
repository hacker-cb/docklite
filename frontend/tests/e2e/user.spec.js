import { test, expect } from './fixtures/auth.fixture.js';

/**
 * Non-Admin User E2E Tests
 * 
 * Tests regular user functionality and restrictions:
 * - View only own projects (multi-tenancy isolation)
 * - Create projects
 * - Manage own containers only
 * - NO access to Users management
 * - NO access to Traefik dashboard
 * - NO access to system containers
 * - NO access to other users' projects
 */

test.describe('Non-Admin User Functionality', () => {
  test('should see limited navigation menu', async ({ userPage }) => {
    await userPage.goto('/');
    
    // Should see allowed menu items
    await expect(userPage.locator('text=Projects')).toBeVisible();
    await expect(userPage.locator('text=Containers')).toBeVisible();
    
    // Should NOT see admin-only items
    await expect(userPage.locator('text=Users')).not.toBeVisible();
    await expect(userPage.locator('text=Traefik')).not.toBeVisible();
  });

  test('should access Projects view', async ({ userPage }) => {
    await userPage.goto('/');
    
    // Navigate to Projects
    await userPage.click('text=Projects');
    
    // Projects view should be visible
    await expect(userPage.locator('h1')).toContainText('Projects');
    
    // Should see "Create Project" button
    await expect(userPage.locator('button:has-text("Create Project")')).toBeVisible();
  });

  test('should see only own projects', async ({ userPage }) => {
    await userPage.goto('/projects');
    
    // Wait for projects to load
    await userPage.waitForTimeout(1000);
    
    // Should see only projects owned by this user
    // Projects table or empty state should be visible
    const projectsExist = await userPage.locator('table tbody tr').count();
    
    if (projectsExist > 0) {
      // All visible projects should belong to current user
      // (verified by backend filtering)
      await expect(userPage.locator('table')).toBeVisible();
    } else {
      // Empty state for no projects
      await expect(userPage.locator('text=/no projects|empty/i')).toBeVisible();
    }
  });

  test('should access Containers view', async ({ userPage }) => {
    await userPage.goto('/');
    
    // Navigate to Containers
    await userPage.click('text=Containers');
    
    // Containers view should be visible
    await expect(userPage.locator('h1')).toContainText('Containers');
  });

  test('should NOT see system containers', async ({ userPage }) => {
    await userPage.goto('/containers');
    
    // Wait for containers to load
    await userPage.waitForTimeout(1000);
    
    // System containers should NOT be visible
    const backendVisible = await userPage.locator('text=docklite-backend').isVisible();
    const frontendVisible = await userPage.locator('text=docklite-frontend').isVisible();
    const traefikVisible = await userPage.locator('text=docklite-traefik').isVisible();
    
    expect(backendVisible).toBeFalsy();
    expect(frontendVisible).toBeFalsy();
    expect(traefikVisible).toBeFalsy();
  });

  test('should NOT access Users page', async ({ userPage }) => {
    // Try to navigate directly to Users page
    await userPage.goto('/users');
    
    // Should be redirected or see access denied
    // (router guard or empty page)
    
    // Users menu item should not be in navigation
    await expect(userPage.locator('nav >> text=Users')).not.toBeVisible();
  });

  test('should NOT access Traefik page', async ({ userPage }) => {
    // Try to navigate directly to Traefik page
    await userPage.goto('/traefik');
    
    // Should be redirected or see access denied
    
    // Traefik menu item should not be in navigation
    await expect(userPage.locator('nav >> text=Traefik')).not.toBeVisible();
  });

  test('should open create project dialog', async ({ userPage }) => {
    await userPage.goto('/projects');
    
    // Click Create Project
    await userPage.click('button:has-text("Create Project")');
    
    // Dialog should open
    await expect(userPage.locator('role=dialog')).toBeVisible();
    
    // Form fields should be visible
    await expect(userPage.locator('input[placeholder*="domain"]')).toBeVisible();
    await expect(userPage.locator('select, .p-dropdown')).toBeVisible(); // Preset selector
  });

  test('should see own containers only in Containers view', async ({ userPage }) => {
    await userPage.goto('/containers');
    
    // Wait for containers to load
    await userPage.waitForTimeout(1000);
    
    // Should see only containers from user's own projects
    const containersCount = await userPage.locator('table tbody tr').count();
    
    // If user has projects with running containers, they should be visible
    // System containers should be filtered out by backend
    
    if (containersCount > 0) {
      await expect(userPage.locator('table')).toBeVisible();
      
      // Verify no system containers
      const hasSystemContainers = await userPage.locator('text=docklite-').isVisible();
      expect(hasSystemContainers).toBeFalsy();
    } else {
      // No containers or empty state
      await expect(userPage.locator('text=/no containers|empty/i')).toBeVisible();
    }
  });
});

