import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/login',
    name: 'Login',
    // No component - handled by App.vue
    meta: { isPublic: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('./views/ProjectsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('./views/UsersView.vue'),
    meta: { requiresAdmin: true, requiresAuth: true }
  },
  {
    path: '/containers',
    name: 'Containers',
    component: () => import('./views/ContainersView.vue'),
    meta: { requiresAdmin: true, requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Navigation guard for auth and admin checks
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  const isAuthenticated = !!token && !!user
  
  // Redirect to login if accessing protected route without auth
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // Redirect to projects if accessing login while authenticated
  if (to.path === '/login' && isAuthenticated) {
    next('/projects')
    return
  }
  
  // Check admin access
  if (to.meta.requiresAdmin) {
    if (!user || !user.is_admin) {
      next('/projects')
      return
    }
  }
  
  next()
})

export default router

