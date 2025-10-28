<template>
  <div class="setup-container">
    <div class="setup-box">
      <div class="setup-header">
        <h1><i class="pi pi-server"></i> DockLite</h1>
        <p>Web Server Management System</p>
        <div class="setup-badge">Initial Setup</div>
      </div>

      <div class="setup-info">
        <i class="pi pi-info-circle"></i>
        <p>Welcome! Let's create your admin account to get started.</p>
      </div>

      <form class="setup-form" @submit.prevent="setup" method="post" action="javascript:void(0)">
        <div class="form-group">
          <label for="username">Username *</label>
          <InputText 
            id="username"
            name="username"
            v-model="userData.username" 
            class="w-full"
            placeholder="admin"
            autocomplete="username"
            @keyup.enter="focusNext('email')"
            autofocus
          />
          <small class="form-hint">Minimum 3 characters</small>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <InputText 
            id="email"
            name="email"
            v-model="userData.email" 
            type="email"
            class="w-full"
            placeholder="admin@example.com (optional)"
            autocomplete="email"
            @keyup.enter="focusNext('password')"
          />
        </div>

        <div class="form-group">
          <label for="password">Password *</label>
          <input 
            id="password"
            name="password"
            v-model="userData.password" 
            type="password"
            class="p-inputtext p-component w-full"
            placeholder="Enter password"
            autocomplete="new-password"
            passwordrules="minlength: 6;"
            @keyup.enter="focusNext('confirmPassword')"
          />
          <small class="form-hint">Minimum 6 characters</small>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password *</label>
          <input 
            id="confirmPassword"
            name="confirm-password"
            v-model="confirmPassword" 
            type="password"
            class="p-inputtext p-component w-full"
            placeholder="Confirm password"
            autocomplete="new-password"
            @keyup.enter="setup"
          />
        </div>

        <button 
          type="submit"
          :disabled="loading"
          class="setup-button w-full"
        >
          <i class="pi pi-check" v-if="!loading"></i>
          <i class="pi pi-spin pi-spinner" v-else></i>
          Create Admin Account
        </button>

        <div v-if="error" class="error-message">
          <i class="pi pi-exclamation-circle"></i>
          {{ error }}
        </div>
      </form>

      <div class="setup-footer">
        <i class="pi pi-shield"></i>
        <p>This account will have full administrator privileges</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authApi } from './api'

const emit = defineEmits(['setup-complete'])

const userData = ref({
  username: '',
  email: '',
  password: ''
})

const confirmPassword = ref('')
const loading = ref(false)
const error = ref(null)

const focusNext = (elementId) => {
  document.getElementById(elementId)?.focus()
}

const validate = () => {
  if (!userData.value.username || userData.value.username.length < 3) {
    error.value = 'Username must be at least 3 characters'
    return false
  }

  if (!userData.value.password || userData.value.password.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return false
  }

  if (userData.value.password !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return false
  }

  return true
}

const setup = async () => {
  error.value = null

  if (!validate()) {
    return
  }

  loading.value = true

  try {
    // Prepare data - convert empty email to null
    const setupData = {
      ...userData.value,
      email: userData.value.email.trim() || null
    }
    
    // Create first admin user
    const response = await authApi.setup(setupData)
    const { access_token } = response.data
    
    // Save token
    localStorage.setItem('token', access_token)
    
    // Get user info
    const userResponse = await authApi.me()
    localStorage.setItem('user', JSON.stringify(userResponse.data))
    
    // Emit success
    emit('setup-complete', userResponse.data)
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
      error.value = err.response?.data?.detail || 'Setup failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.setup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.setup-box {
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.setup-header {
  text-align: center;
  margin-bottom: 2rem;
}

.setup-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.setup-header p {
  margin: 0.5rem 0 0 0;
  color: #666;
}

.setup-badge {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.setup-info {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.setup-info i {
  color: #2196f3;
  font-size: 1.5rem;
}

.setup-info p {
  margin: 0;
  color: #1565c0;
  font-weight: 500;
}

.setup-form {
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

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #999;
}

.w-full {
  width: 100%;
}

.setup-button {
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

.setup-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.setup-button:disabled {
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

.setup-footer {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.setup-footer i {
  color: #667eea;
}

.setup-footer p {
  margin: 0;
}
</style>

