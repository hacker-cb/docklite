import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useProjects } from '../../src/composables/useProjects'
import { projectsApi } from '../../src/api'

// Mock API
vi.mock('../../src/api', () => ({
  projectsApi: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getById: vi.fn(),
    getEnv: vi.fn(),
    updateEnv: vi.fn()
  }
}))

describe('useProjects Composable', () => {
  let composable

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Create new composable instance for each test
    composable = useProjects()
  })

  describe('Initial state', () => {
    it('should have empty projects array', () => {
      expect(composable.projects.value).toEqual([])
    })

    it('should not be loading initially', () => {
      expect(composable.loading.value).toBe(false)
    })

    it('should have no error initially', () => {
      expect(composable.error.value).toBeNull()
    })
  })

  describe('loadProjects', () => {
    it('should load projects successfully', async () => {
      const mockProjects = [
        { id: 1, name: 'project1' },
        { id: 2, name: 'project2' }
      ]
      projectsApi.getAll.mockResolvedValue({
        data: { projects: mockProjects }
      })

      await composable.loadProjects()

      expect(composable.projects.value).toEqual(mockProjects)
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
    })

    it('should set loading state during fetch', async () => {
      projectsApi.getAll.mockImplementation(() => {
        expect(composable.loading.value).toBe(true)
        return Promise.resolve({ data: { projects: [] } })
      })

      await composable.loadProjects()
      expect(composable.loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Failed to load')
      projectsApi.getAll.mockRejectedValue(mockError)

      await expect(composable.loadProjects()).rejects.toThrow('Failed to load')
      expect(composable.error.value).toBe(mockError)
      expect(composable.loading.value).toBe(false)
    })
  })

  describe('createProject', () => {
    it('should create project and reload list', async () => {
      const newProject = { name: 'new-project', domain: 'test.local' }
      const createdProject = { id: 3, ...newProject }
      
      projectsApi.create.mockResolvedValue({ data: createdProject })
      projectsApi.getAll.mockResolvedValue({ data: { projects: [createdProject] } })

      const result = await composable.createProject(newProject)

      expect(result).toEqual(createdProject)
      expect(projectsApi.create).toHaveBeenCalledWith(newProject)
      expect(projectsApi.getAll).toHaveBeenCalled()
    })

    it('should handle create errors', async () => {
      const mockError = new Error('Create failed')
      projectsApi.create.mockRejectedValue(mockError)

      await expect(composable.createProject({})).rejects.toThrow('Create failed')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('updateProject', () => {
    it('should update project and reload list', async () => {
      const updatedData = { name: 'updated-name' }
      const updatedProject = { id: 1, ...updatedData }
      
      projectsApi.update.mockResolvedValue({ data: updatedProject })
      projectsApi.getAll.mockResolvedValue({ data: { projects: [updatedProject] } })

      await composable.updateProject(1, updatedData)

      expect(projectsApi.update).toHaveBeenCalledWith(1, updatedData)
      expect(projectsApi.getAll).toHaveBeenCalled()
    })
  })

  describe('deleteProject', () => {
    it('should delete project and reload list', async () => {
      projectsApi.delete.mockResolvedValue({})
      projectsApi.getAll.mockResolvedValue({ data: { projects: [] } })

      await composable.deleteProject(1)

      expect(projectsApi.delete).toHaveBeenCalledWith(1)
      expect(projectsApi.getAll).toHaveBeenCalled()
    })
  })

  describe('getProject', () => {
    it('should get project by ID', async () => {
      const project = { id: 1, name: 'test' }
      projectsApi.getById.mockResolvedValue({ data: project })

      const result = await composable.getProject(1)

      expect(result).toEqual(project)
      expect(projectsApi.getById).toHaveBeenCalledWith(1)
    })
  })

  describe('getEnvVars', () => {
    it('should get environment variables', async () => {
      const envVars = { KEY: 'value' }
      projectsApi.getEnv.mockResolvedValue({ data: envVars })

      const result = await composable.getEnvVars(1)

      expect(result).toEqual(envVars)
      expect(projectsApi.getEnv).toHaveBeenCalledWith(1)
    })
  })

  describe('updateEnvVars', () => {
    it('should update environment variables', async () => {
      const envVars = { KEY: 'newvalue' }
      projectsApi.updateEnv.mockResolvedValue({})

      await composable.updateEnvVars(1, envVars)

      expect(projectsApi.updateEnv).toHaveBeenCalledWith(1, envVars)
    })
  })
})

