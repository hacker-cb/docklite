/**
 * Containers composable - manages Docker container operations
 */
import { ref } from 'vue'
import { containersApi } from '../api'
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '../config/constants'

export function useContainers() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Start container for project
   * @param {number} projectId - Project ID
   */
  const startContainer = async (projectId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await containersApi.start(projectId)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Stop container for project
   * @param {number} projectId - Project ID
   */
  const stopContainer = async (projectId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await containersApi.stop(projectId)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Restart container for project
   * @param {number} projectId - Project ID
   */
  const restartContainer = async (projectId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await containersApi.restart(projectId)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get container status for project
   * @param {number} projectId - Project ID
   */
  const getContainerStatus = async (projectId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await containersApi.getStatus(projectId)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    loading,
    error,
    
    // Methods
    startContainer,
    stopContainer,
    restartContainer,
    getContainerStatus
  }
}

