<template>
  <div class="app">
    <!-- Setup screen (first time) -->
    <Setup v-if="needsSetup && !isAuthenticated" @setup-complete="handleLoginSuccess" />

    <!-- Login screen -->
    <Login v-else-if="!isAuthenticated" @login-success="handleLoginSuccess" />

    <!-- Main app (authenticated) -->
    <div v-else>
      <header class="header">
        <div class="header-content">
          <div class="header-left">
            <h1><i class="pi pi-server"></i> DockLite</h1>
            <p>Web Server Management System</p>
          </div>
          <div class="header-right">
            <span class="user-info">
              <i class="pi pi-user"></i>
              {{ currentUser?.username }}
            </span>
            <Button 
              label="Logout" 
              icon="pi pi-sign-out" 
              @click="handleLogout"
              class="p-button-sm p-button-outlined"
            />
          </div>
        </div>
      </header>

      <main class="main-content">
      <!-- Navigation Tabs -->
      <div class="nav-tabs">
        <Button 
          label="Projects"
          icon="pi pi-server" 
          @click="router.push('/projects')"
          :class="$route.path === '/projects' ? 'p-button-primary' : 'p-button-outlined'"
        />
        <Button 
          v-if="currentUser?.is_admin"
          label="Users"
          icon="pi pi-users" 
          @click="router.push('/users')"
          :class="$route.path === '/users' ? 'p-button-primary' : 'p-button-outlined'"
        />
        <Button 
          v-if="currentUser?.is_admin"
          label="Dashboard"
          icon="pi pi-chart-line" 
          @click="openDashboard"
          class="p-button-outlined p-button-secondary"
        />
      </div>

      <!-- Router View -->
      <router-view />
    </main>
    </div>

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from './api'
import Login from './Login.vue'
import Setup from './Setup.vue'

const router = useRouter()

// Auth state
const isAuthenticated = ref(false)
const currentUser = ref(null)
const needsSetup = ref(false)

const checkSetup = async () => {
  try {
    const response = await authApi.checkSetup()
    needsSetup.value = response.data.setup_needed
  } catch (error) {
    console.error('Failed to check setup status:', error)
  }
}

const checkAuth = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    isAuthenticated.value = false
    await checkSetup()
    return
  }

  try {
    const response = await authApi.me()
    currentUser.value = response.data
    isAuthenticated.value = true
    needsSetup.value = false
  } catch (error) {
    // Token invalid, clear it
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    await checkSetup()
  }
}

const handleLoginSuccess = (user) => {
  currentUser.value = user
  isAuthenticated.value = true
  needsSetup.value = false
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (error) {
    // Ignore errors on logout
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Clear token cookie
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax'
    
    isAuthenticated.value = false
    currentUser.value = null
    router.push('/projects')
  }
}

const openDashboard = () => {
  // Open Traefik dashboard in new tab
  // Auth is handled automatically via JWT token in cookies/local storage
  window.open('/dashboard/', '_blank')
}

onMounted(() => {
  checkAuth()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f8f9fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left h1 {
  margin: 0;
  font-size: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-left p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-weight: 500;
}

.main-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}
</style>
