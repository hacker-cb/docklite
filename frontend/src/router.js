import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('./views/ProjectsView.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('./views/UsersView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/containers',
    name: 'Containers',
    component: () => import('./views/ContainersView.vue'),
    meta: { requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Navigation guard для admin проверки
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAdmin) {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    
    if (!user || !user.is_admin) {
      next('/projects')
      return
    }
  }
  next()
})

export default router

