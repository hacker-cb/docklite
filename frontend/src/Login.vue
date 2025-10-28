<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1><i class="pi pi-server"></i> DockLite</h1>
        <p>Web Server Management System</p>
      </div>

      <form class="login-form" @submit.prevent="login">
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

        <Button 
          type="submit"
          label="Login" 
          icon="pi pi-sign-in" 
          :loading="loading"
          class="w-full login-button"
        />

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
    
    // Save token
    localStorage.setItem('token', access_token)
    
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

