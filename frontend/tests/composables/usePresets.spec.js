import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePresets } from '../../src/composables/usePresets'

// Mock API
const mockPresetsApi = {
  getAll: vi.fn(),
  getCategories: vi.fn(),
  getById: vi.fn()
}

vi.mock('../../src/api', () => ({
  presetsApi: mockPresetsApi
}))

describe('usePresets Composable', () => {
  let composable

  beforeEach(() => {
    vi.clearAllMocks()
    composable = usePresets()
  })

  describe('Initial state', () => {
    it('should have empty presets array', () => {
      expect(composable.presets.value).toEqual([])
    })

    it('should have empty categories array', () => {
      expect(composable.categories.value).toEqual([])
    })

    it('should not be loading initially', () => {
      expect(composable.loading.value).toBe(false)
    })

    it('should have selectedCategory set to "all"', () => {
      expect(composable.selectedCategory.value).toBe('all')
    })

    it('should have no preset selected initially', () => {
      expect(composable.selectedPreset.value).toBeNull()
      expect(composable.presetDetails.value).toBeNull()
    })
  })

  describe('loadPresets', () => {
    it('should load presets and categories', async () => {
      const mockPresets = [
        { id: 'nginx', name: 'Nginx', category: 'web' },
        { id: 'postgres', name: 'PostgreSQL', category: 'database' }
      ]
      const mockCategories = [
        { id: 'web', name: 'Web Servers', count: 1 },
        { id: 'database', name: 'Databases', count: 1 }
      ]

      mockPresetsApi.getAll.mockResolvedValue({ data: mockPresets })
      mockPresetsApi.getCategories.mockResolvedValue({ data: mockCategories })

      await composable.loadPresets()

      expect(composable.presets.value).toEqual(mockPresets)
      expect(composable.categories.value).toEqual(mockCategories)
      expect(composable.loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const mockError = new Error('Load failed')
      mockPresetsApi.getAll.mockRejectedValue(mockError)
      mockPresetsApi.getCategories.mockRejectedValue(mockError)

      await expect(composable.loadPresets()).rejects.toThrow('Load failed')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('filteredPresets computed', () => {
    beforeEach(() => {
      composable.presets.value = [
        { id: 'nginx', category: 'web' },
        { id: 'apache', category: 'web' },
        { id: 'postgres', category: 'database' }
      ]
    })

    it('should return all presets when category is "all"', () => {
      composable.selectedCategory.value = 'all'
      expect(composable.filteredPresets.value).toHaveLength(3)
    })

    it('should filter presets by category', () => {
      composable.selectedCategory.value = 'web'
      expect(composable.filteredPresets.value).toHaveLength(2)
      expect(composable.filteredPresets.value.every(p => p.category === 'web')).toBe(true)
    })

    it('should return empty array for non-existent category', () => {
      composable.selectedCategory.value = 'nonexistent'
      expect(composable.filteredPresets.value).toHaveLength(0)
    })
  })

  describe('presetComposeContent computed', () => {
    it('should return empty string when no preset details', () => {
      expect(composable.presetComposeContent.value).toBe('')
    })

    it('should return compose content from preset details', () => {
      const composeContent = 'version: "3.8"\nservices:\n  web:\n    image: nginx'
      composable.presetDetails.value = { compose_content: composeContent }
      expect(composable.presetComposeContent.value).toBe(composeContent)
    })
  })

  describe('selectCategory', () => {
    it('should change selected category', () => {
      composable.selectCategory('web')
      expect(composable.selectedCategory.value).toBe('web')
    })
  })

  describe('selectPreset', () => {
    beforeEach(() => {
      composable.presets.value = [
        { id: 'nginx', name: 'Nginx', category: 'web' }
      ]
    })

    it('should select preset and load details', async () => {
      const mockDetails = {
        id: 'nginx',
        compose_content: 'version: "3.8"'
      }
      mockPresetsApi.getById.mockResolvedValue({ data: mockDetails })

      await composable.selectPreset('nginx')

      expect(composable.presetDetails.value).toEqual(mockDetails)
      expect(composable.selectedPreset.value).toEqual({ id: 'nginx', name: 'Nginx', category: 'web' })
      expect(mockPresetsApi.getById).toHaveBeenCalledWith('nginx')
    })

    it('should handle errors', async () => {
      const mockError = new Error('Preset not found')
      mockPresetsApi.getById.mockRejectedValue(mockError)

      await expect(composable.selectPreset('nonexistent')).rejects.toThrow('Preset not found')
      expect(composable.error.value).toBe(mockError)
    })
  })

  describe('resetSelection', () => {
    it('should reset all selections', () => {
      composable.selectedCategory.value = 'web'
      composable.selectedPreset.value = { id: 'nginx' }
      composable.presetDetails.value = { compose_content: 'test' }

      composable.resetSelection()

      expect(composable.selectedCategory.value).toBe('all')
      expect(composable.selectedPreset.value).toBeNull()
      expect(composable.presetDetails.value).toBeNull()
    })
  })
})

