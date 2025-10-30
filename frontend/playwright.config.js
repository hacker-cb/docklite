import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Configuration for DockLite
 * 
 * Tests admin and non-admin user flows:
 * - Authentication
 * - Projects management
 * - Containers management
 * - Users management (admin only)
 * - Traefik access (admin only)
 * - Multi-tenancy isolation
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  // Maximum time one test can run
  timeout: 10 * 1000,
  
  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html'],
    ['list']
  ],
  
  // Shared settings for all projects
  use: {
    // Base URL for tests
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // No persistent storage between tests
    storageState: undefined,
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    // Uncomment to test on more browsers
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Assume DockLite is already running
  // Run `./docklite start` before tests
  webServer: {
    command: 'echo "Assuming DockLite is already running..."',
    url: 'http://localhost',
    timeout: 5 * 1000,
    reuseExistingServer: true,
  },
});

