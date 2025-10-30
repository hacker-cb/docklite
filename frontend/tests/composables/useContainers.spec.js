import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useContainers } from '../../src/composables/useContainers'
import { containersApi } from '../../src/api'

// Mock API
vi.mock('../../src/api', () => ({
  containersApi: {
    start: vi.fn(),
    stop: vi.fn(),
    restart: vi.fn(),
    getStatus: vi.fn()
  }
}))

describe('useContainers Composable', () => {
  let composable

  beforeEach(() => {
    vi.clearAllMocks()
    composable = useContainers()
  })

  describe('Initial state', () => {
    it('should not be loading initially', () => {
      expect(composable.loading.value).toBe(false)
    })

    it('should have no error initially', () => {
      expect(composable.error.value).toBeNull()
    })
  })

  describe('startContainer', () => {
    it('should start container successfully', async () => {
      const mockResponse = { status: 'running', message: 'Started' }
      mockContainersApi.start.mockResolvedValue({ data: mockResponse })

      const result = await composable.startContainer(1)

      expect(result).toEqual(mockResponse)
      expect(mockContainersApi.start).toHaveBeenCalledWith(1)
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
    })

    it('should set loading state', async () => {
      mockContainersApi.start.mockImplementation(() => {
        expect(composable.loading.value).toBe(true)
        return Promise.resolve({ data: {} })
      })

      await composable.startContainer(1)
      expect(composable.loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Start failed')
      mockContainersApi.start.mockRejectedValue(mockError)

      await expect(composable.startContainer(1)).rejects.toThrow('Start failed')
      expect(composable.error.value).toBe(mockError)
      expect(composable.loading.value).toBe(false)
    })
  })

  describe('stopContainer', () => {
    it('should stop container successfully', async () => {
      const mockResponse = { status: 'stopped', message: 'Stopped' }
      mockContainersApi.stop.mockResolvedValue({ data: mockResponse })

      const result = await composable.stopContainer(1)

      expect(result).toEqual(mockResponse)
      expect(mockContainersApi.stop).toHaveBeenCalledWith(1)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Stop failed')
      mockContainersApi.stop.mockRejectedValue(mockError)

      await expect(composable.stopContainer(1)).rejects.toThrow('Stop failed')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('restartContainer', () => {
    it('should restart container successfully', async () => {
      const mockResponse = { status: 'running', message: 'Restarted' }
      mockContainersApi.restart.mockResolvedValue({ data: mockResponse })

      const result = await composable.restartContainer(1)

      expect(result).toEqual(mockResponse)
      expect(mockContainersApi.restart).toHaveBeenCalledWith(1)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Restart failed')
      mockContainersApi.restart.mockRejectedValue(mockError)

      await expect(composable.restartContainer(1)).rejects.toThrow('Restart failed')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('getContainerStatus', () => {
    it('should get container status successfully', async () => {
      const mockStatus = { status: 'running', uptime: '2 hours' }
      mockContainersApi.getStatus.mockResolvedValue({ data: mockStatus })

      const result = await composable.getContainerStatus(1)

      expect(result).toEqual(mockStatus)
      expect(mockContainersApi.getStatus).toHaveBeenCalledWith(1)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Status check failed')
      mockContainersApi.getStatus.mockRejectedValue(mockError)

      await expect(composable.getContainerStatus(1)).rejects.toThrow('Status check failed')
      expect(composable.error.value).toBe(mockError)
    })
  })
})

