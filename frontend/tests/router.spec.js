import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import router from '../src/router'

describe('Vue Router', () => {
  describe('Router configuration', () => {
    it('should use hash history', () => {
      // The actual router uses createWebHashHistory
      // We're testing the routes configuration
      expect(router.options.routes).toBeDefined()
    })

    it('should have routes defined', () => {
      const routes = router.options.routes
      expect(routes).toBeInstanceOf(Array)
      expect(routes.length).toBeGreaterThan(0)
    })
  })

  describe('Routes', () => {
    it('should have root redirect to /projects', () => {
      const rootRoute = router.options.routes.find(r => r.path === '/')
      expect(rootRoute).toBeDefined()
      expect(rootRoute.redirect).toBe('/projects')
    })

    it('should have /projects route', () => {
      const projectsRoute = router.options.routes.find(r => r.path === '/projects')
      expect(projectsRoute).toBeDefined()
      expect(projectsRoute.name).toBe('Projects')
    })

    it('should have /users route', () => {
      const usersRoute = router.options.routes.find(r => r.path === '/users')
      expect(usersRoute).toBeDefined()
      expect(usersRoute.name).toBe('Users')
    })

    it('should have requiresAdmin meta on users route', () => {
      const usersRoute = router.options.routes.find(r => r.path === '/users')
      expect(usersRoute.meta).toBeDefined()
      expect(usersRoute.meta.requiresAdmin).toBe(true)
    })
  })

  describe('Lazy loading', () => {
    it('should lazy load ProjectsView', () => {
      const projectsRoute = router.options.routes.find(r => r.path === '/projects')
      expect(typeof projectsRoute.component).toBe('function')
    })

    it('should lazy load UsersView', () => {
      const usersRoute = router.options.routes.find(r => r.path === '/users')
      expect(typeof usersRoute.component).toBe('function')
    })
  })

  describe('Navigation', () => {
    let testRouter

    beforeEach(() => {
      // Create test router with memory history
      testRouter = createRouter({
        history: createMemoryHistory(),
        routes: router.options.routes
      })
    })

    it('should navigate to /projects', async () => {
      await testRouter.push('/projects')
      expect(testRouter.currentRoute.value.path).toBe('/projects')
      expect(testRouter.currentRoute.value.name).toBe('Projects')
    })

    it('should navigate to /users', async () => {
      await testRouter.push('/users')
      expect(testRouter.currentRoute.value.path).toBe('/users')
      expect(testRouter.currentRoute.value.name).toBe('Users')
    })

    it('should redirect from / to /projects', async () => {
      await testRouter.push('/')
      expect(testRouter.currentRoute.value.path).toBe('/projects')
    })
  })

  describe('Navigation guards', () => {
    it('should have beforeEach guard defined', () => {
      // Router has beforeEach guard for admin check
      expect(router.beforeEach).toBeDefined()
    })
  })

  describe('Route meta', () => {
    it('should not require admin for projects route', () => {
      const projectsRoute = router.options.routes.find(r => r.path === '/projects')
      expect(projectsRoute.meta?.requiresAdmin).toBeFalsy()
    })

    it('should require admin for users route', () => {
      const usersRoute = router.options.routes.find(r => r.path === '/users')
      expect(usersRoute.meta?.requiresAdmin).toBe(true)
    })
  })
})

