/**
 * Projects composable - manages project CRUD operations
 */
import { ref } from 'vue'
import { projectsApi } from '../api'
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '../config/constants'

export function useProjects() {
  const projects = ref([])
  const loading = ref(false)
  const error = ref(null)

  /**
   * Load all projects
   */
  const loadProjects = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await projectsApi.getAll()
      projects.value = response.data.projects
      return projects.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new project
   * @param {object} projectData - Project data
   */
  const createProject = async (projectData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await projectsApi.create(projectData)
      await loadProjects() // Reload list
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update existing project
   * @param {number} id - Project ID
   * @param {object} projectData - Updated project data
   */
  const updateProject = async (id, projectData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await projectsApi.update(id, projectData)
      await loadProjects() // Reload list
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete project
   * @param {number} id - Project ID
   */
  const deleteProject = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await projectsApi.delete(id)
      await loadProjects() // Reload list
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get project by ID
   * @param {number} id - Project ID
   */
  const getProject = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await projectsApi.getById(id)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get environment variables for project
   * @param {number} id - Project ID
   */
  const getEnvVars = async (id) => {
    try {
      const response = await projectsApi.getEnv(id)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    }
  }

  /**
   * Update environment variables for project
   * @param {number} id - Project ID
   * @param {object} envVars - Environment variables
   */
  const updateEnvVars = async (id, envVars) => {
    try {
      await projectsApi.updateEnv(id, envVars)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  return {
    // State
    projects,
    loading,
    error,
    
    // Methods
    loadProjects,
    createProject,
    updateProject,
    deleteProject,
    getProject,
    getEnvVars,
    updateEnvVars
  }
}

