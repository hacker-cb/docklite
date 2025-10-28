/**
 * Presets composable - manages preset operations
 */
import { ref, computed } from 'vue'
import { presetsApi } from '../api'

export function usePresets() {
  const presets = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)
  const selectedCategory = ref('all')
  const selectedPreset = ref(null)
  const presetDetails = ref(null)

  /**
   * Computed: filtered presets by category
   */
  const filteredPresets = computed(() => {
    if (selectedCategory.value === 'all') {
      return presets.value
    }
    return presets.value.filter(p => p.category === selectedCategory.value)
  })

  /**
   * Computed: preset compose content
   */
  const presetComposeContent = computed(() => {
    return presetDetails.value?.compose_content || ''
  })

  /**
   * Load all presets and categories
   */
  const loadPresets = async () => {
    loading.value = true
    error.value = null
    
    try {
      const [presetsRes, categoriesRes] = await Promise.all([
        presetsApi.getAll(),
        presetsApi.getCategories()
      ])
      presets.value = presetsRes.data
      categories.value = categoriesRes.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Select category
   * @param {string} categoryId - Category ID
   */
  const selectCategory = (categoryId) => {
    selectedCategory.value = categoryId
  }

  /**
   * Select preset and load details
   * @param {string} presetId - Preset ID
   */
  const selectPreset = async (presetId) => {
    try {
      const response = await presetsApi.getById(presetId)
      presetDetails.value = response.data
      selectedPreset.value = presets.value.find(p => p.id === presetId)
      return response.data
    } catch (err) {
      error.value = err
      throw err
    }
  }

  /**
   * Reset preset selection
   */
  const resetSelection = () => {
    selectedCategory.value = 'all'
    selectedPreset.value = null
    presetDetails.value = null
  }

  return {
    // State
    presets,
    categories,
    loading,
    error,
    selectedCategory,
    selectedPreset,
    presetDetails,
    
    // Computed
    filteredPresets,
    presetComposeContent,
    
    // Methods
    loadPresets,
    selectCategory,
    selectPreset,
    resetSelection
  }
}

