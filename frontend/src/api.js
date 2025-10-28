import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export const projectsApi = {
  // Get all projects
  getAll() {
    return api.get('/projects')
  },
  
  // Get project by ID
  getById(id) {
    return api.get(`/projects/${id}`)
  },
  
  // Create new project
  create(projectData) {
    return api.post('/projects', projectData)
  },
  
  // Update project
  update(id, projectData) {
    return api.put(`/projects/${id}`, projectData)
  },
  
  // Delete project
  delete(id) {
    return api.delete(`/projects/${id}`)
  },
  
  // Get project environment variables
  getEnv(id) {
    return api.get(`/projects/${id}/env`)
  },
  
  // Update project environment variables
  updateEnv(id, envVars) {
    return api.put(`/projects/${id}/env`, envVars)
  }
}

export const presetsApi = {
  // Get all presets
  getAll(category = null) {
    const params = category ? { category } : {}
    return api.get('/presets', { params })
  },
  
  // Get preset categories
  getCategories() {
    return api.get('/presets/categories')
  },
  
  // Get preset by ID with full details
  getById(id) {
    return api.get(`/presets/${id}`)
  }
}

export const deploymentApi = {
  // Get deployment instructions for project
  getInfo(projectId) {
    return api.get(`/deployment/${projectId}/info`)
  },
  
  // Get SSH setup instructions
  getSshSetup() {
    return api.get('/deployment/ssh-setup')
  }
}

export const authApi = {
  // Check if setup is needed
  checkSetup() {
    return api.get('/auth/setup/check')
  },
  
  // Initial setup (create first admin)
  setup(userData) {
    return api.post('/auth/setup', userData)
  },
  
  // Login
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  
  // Get current user
  me() {
    return api.get('/auth/me')
  },
  
  // Logout
  logout() {
    return api.post('/auth/logout')
  }
}

export const usersApi = {
  // Get all users
  getAll() {
    return api.get('/users')
  },
  
  // Get user by ID
  getById(id) {
    return api.get(`/users/${id}`)
  },
  
  // Create new user
  create(userData) {
    return api.post('/users', userData)
  },
  
  // Update user (is_active, is_admin)
  update(id, data) {
    return api.put(`/users/${id}`, null, { params: data })
  },
  
  // Delete user
  delete(id) {
    return api.delete(`/users/${id}`)
  },
  
  // Change password
  changePassword(id, newPassword) {
    return api.put(`/users/${id}/password`, null, { params: { new_password: newPassword } })
  }
}

export default api

