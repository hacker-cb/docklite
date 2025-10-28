import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useProjects } from '../../src/composables/useProjects'

// Mock API
const mockProjectsApi = {
  getAll: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  delete: vi.fn(),
  getById: vi.fn(),
  getEnv: vi.fn(),
  updateEnv: vi.fn()
}

vi.mock('../../src/api', () => ({
  projectsApi: mockProjectsApi
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
      mockProjectsApi.getAll.mockResolvedValue({
        data: { projects: mockProjects }
      })

      await composable.loadProjects()

      expect(composable.projects.value).toEqual(mockProjects)
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
    })

    it('should set loading state during fetch', async () => {
      mockProjectsApi.getAll.mockImplementation(() => {
        expect(composable.loading.value).toBe(true)
        return Promise.resolve({ data: { projects: [] } })
      })

      await composable.loadProjects()
      expect(composable.loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Failed to load')
      mockProjectsApi.getAll.mockRejectedValue(mockError)

      await expect(composable.loadProjects()).rejects.toThrow('Failed to load')
      expect(composable.error.value).toBe(mockError)
      expect(composable.loading.value).toBe(false)
    })
  })

  describe('createProject', () => {
    it('should create project and reload list', async () => {
      const newProject = { name: 'new-project', domain: 'test.local' }
      const createdProject = { id: 3, ...newProject }
      
      mockProjectsApi.create.mockResolvedValue({ data: createdProject })
      mockProjectsApi.getAll.mockResolvedValue({ data: { projects: [createdProject] } })

      const result = await composable.createProject(newProject)

      expect(result).toEqual(createdProject)
      expect(mockProjectsApi.create).toHaveBeenCalledWith(newProject)
      expect(mockProjectsApi.getAll).toHaveBeenCalled()
    })

    it('should handle create errors', async () => {
      const mockError = new Error('Create failed')
      mockProjectsApi.create.mockRejectedValue(mockError)

      await expect(composable.createProject({})).rejects.toThrow('Create failed')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('updateProject', () => {
    it('should update project and reload list', async () => {
      const updatedData = { name: 'updated-name' }
      const updatedProject = { id: 1, ...updatedData }
      
      mockProjectsApi.update.mockResolvedValue({ data: updatedProject })
      mockProjectsApi.getAll.mockResolvedValue({ data: { projects: [updatedProject] } })

      await composable.updateProject(1, updatedData)

      expect(mockProjectsApi.update).toHaveBeenCalledWith(1, updatedData)
      expect(mockProjectsApi.getAll).toHaveBeenCalled()
    })
  })

  describe('deleteProject', () => {
    it('should delete project and reload list', async () => {
      mockProjectsApi.delete.mockResolvedValue({})
      mockProjectsApi.getAll.mockResolvedValue({ data: { projects: [] } })

      await composable.deleteProject(1)

      expect(mockProjectsApi.delete).toHaveBeenCalledWith(1)
      expect(mockProjectsApi.getAll).toHaveBeenCalled()
    })
  })

  describe('getProject', () => {
    it('should get project by ID', async () => {
      const project = { id: 1, name: 'test' }
      mockProjectsApi.getById.mockResolvedValue({ data: project })

      const result = await composable.getProject(1)

      expect(result).toEqual(project)
      expect(mockProjectsApi.getById).toHaveBeenCalledWith(1)
    })
  })

  describe('getEnvVars', () => {
    it('should get environment variables', async () => {
      const envVars = { KEY: 'value' }
      mockProjectsApi.getEnv.mockResolvedValue({ data: envVars })

      const result = await composable.getEnvVars(1)

      expect(result).toEqual(envVars)
      expect(mockProjectsApi.getEnv).toHaveBeenCalledWith(1)
    })
  })

  describe('updateEnvVars', () => {
    it('should update environment variables', async () => {
      const envVars = { KEY: 'newvalue' }
      mockProjectsApi.updateEnv.mockResolvedValue({})

      await composable.updateEnvVars(1, envVars)

      expect(mockProjectsApi.updateEnv).toHaveBeenCalledWith(1, envVars)
    })
  })
})

