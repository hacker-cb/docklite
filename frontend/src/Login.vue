<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1><i class="pi pi-server"></i> DockLite</h1>
        <p>Web Server Management System</p>
      </div>

      <form class="login-form" @submit.prevent="login" method="post" action="javascript:void(0)">
        <div class="form-group">
          <label for="username">Username</label>
          <InputText 
            id="username"
            name="username"
            v-model="credentials.username" 
            class="w-full"
            placeholder="Enter username"
            autocomplete="username"
            autofocus
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <InputText 
            id="password"
            name="password"
            v-model="credentials.password" 
            type="password"
            class="w-full"
            placeholder="Enter password"
            autocomplete="current-password"
            @keyup.enter="login"
          />
        </div>

        <button 
          type="submit"
          :disabled="loading"
          class="login-button w-full"
        >
          <i class="pi pi-sign-in" v-if="!loading"></i>
          <i class="pi pi-spin pi-spinner" v-else></i>
          Login
        </button>

        <div v-if="error" class="error-message">
          <i class="pi pi-exclamation-circle"></i>
          {{ error }}
        </div>
      </form>

      <div class="login-footer">
        <p>Enter your DockLite credentials</p>
        <small>Forgot password? Contact your administrator</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authApi } from './api'

const emit = defineEmits(['login-success'])

const credentials = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

const login = async () => {
  if (!credentials.value.username || !credentials.value.password) {
    error.value = 'Please enter username and password'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await authApi.login(credentials.value)
    const { access_token } = response.data
    
    // Save token to localStorage
    localStorage.setItem('token', access_token)
    
    // Also save to cookie for Traefik ForwardAuth (dashboard access)
    document.cookie = `token=${access_token}; path=/; max-age=2592000; SameSite=Lax`
    
    // Get user info
    const userResponse = await authApi.me()
    localStorage.setItem('user', JSON.stringify(userResponse.data))
    
    // Emit success
    emit('login-success', userResponse.data)
  } catch (err) {
    // Handle validation errors from FastAPI
    if (err.response?.status === 422 && err.response?.data?.detail) {
      const details = err.response.data.detail
      if (Array.isArray(details)) {
        // Extract field errors
        const fieldErrors = details.map(d => {
          const field = d.loc?.[d.loc.length - 1] || 'field'
          return `${field}: ${d.msg}`
        }).join(', ')
        error.value = fieldErrors
      } else {
        error.value = details
      }
    } else {
      error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.login-header p {
  margin: 0.5rem 0 0 0;
  color: #666;
}

.login-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.w-full {
  width: 100%;
}

.login-button {
  margin-top: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.75rem 1.25rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: inherit;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c33;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.login-footer {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.875rem;
}

.login-footer code {
  background: #f0f0f0;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85rem;
}

.login-footer p {
  margin: 0.5rem 0;
}

.login-footer small {
  color: #999;
  display: block;
  margin-top: 0.75rem;
}
</style>

