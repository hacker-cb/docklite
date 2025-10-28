import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

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

export default api

