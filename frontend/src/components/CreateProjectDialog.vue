<template>
  <Dialog 
    v-model:visible="visible" 
    :header="editingProject ? 'Edit Project' : 'Create New Project'"
    :modal="true"
    :style="{ width: '900px' }"
    :maximizable="true"
    @hide="handleClose"
  >
    <TabView v-if="!editingProject">
      <TabPanel header="From Preset">
        <!-- Categories -->
        <div class="categories-bar">
          <Chip 
            v-for="cat in categories" 
            :key="cat.id"
            :label="`${cat.name} (${cat.count})`"
            :class="{'selected-category': selectedCategory === cat.id}"
            @click="selectCategory(cat.id)"
            class="category-chip"
          />
        </div>

        <!-- Presets Grid -->
        <div class="presets-grid" v-if="!loadingPresets">
          <Card 
            v-for="preset in filteredPresets" 
            :key="preset.id"
            class="preset-card"
            :class="{'selected-preset': selectedPreset?.id === preset.id}"
            @click="selectPreset(preset.id)"
          >
            <template #header>
              <div class="preset-icon">{{ preset.icon }}</div>
            </template>
            <template #title>{{ preset.name }}</template>
            <template #content>
              <p class="preset-description">{{ preset.description }}</p>
              <div class="preset-tags">
                <Chip 
                  v-for="tag in preset.tags" 
                  :key="tag" 
                  :label="tag" 
                  class="preset-tag"
                />
              </div>
            </template>
          </Card>
        </div>
        
        <div v-else class="presets-loading">
          <Skeleton v-for="i in 6" :key="i" height="200px" class="preset-skeleton" />
        </div>
      </TabPanel>

      <TabPanel header="Custom">
        <div class="form-group">
          <label>Docker Compose Content *</label>
          <Textarea 
            v-model="formData.compose_content" 
            rows="15" 
            class="w-full"
            style="font-family: monospace; font-size: 12px;"
            placeholder="version: '3.8'&#10;services:&#10;  web:&#10;    image: nginx:alpine&#10;    ports:&#10;      - '80:80'"
          />
        </div>
      </TabPanel>
    </TabView>

    <!-- Project Details Form -->
    <div class="form-section">
      <h3>Project Details</h3>
      
      <div class="form-group">
        <label>Project Name *</label>
        <InputText v-model="formData.name" class="w-full" placeholder="my-awesome-project" />
      </div>

      <div class="form-group">
        <label>Domain *</label>
        <InputText v-model="formData.domain" class="w-full" placeholder="example.com" />
        <small class="form-hint">Проект будет доступен через Traefik по этому домену</small>
      </div>
    </div>

    <!-- Preview for editing -->
    <div v-if="editingProject" class="form-group">
      <label>Docker Compose Content *</label>
      <Textarea 
        v-model="formData.compose_content" 
        rows="10" 
        class="w-full"
        style="font-family: monospace; font-size: 12px;"
      />
    </div>

    <!-- Preview for preset selection -->
    <div v-if="selectedPreset && !editingProject" class="preview-section">
      <h3>Preview</h3>
      <Textarea 
        :value="presetComposeContent" 
        rows="10" 
        class="w-full"
        style="font-family: monospace; font-size: 12px;"
        readonly
      />
    </div>

    <template #footer>
      <Button 
        label="Cancel" 
        icon="pi pi-times" 
        @click="handleClose" 
        class="p-button-text"
      />
      <Button 
        :label="editingProject ? 'Update' : 'Create'" 
        icon="pi pi-check" 
        @click="handleSave"
        :loading="saving"
        :disabled="!canSave"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useProjects } from '../composables/useProjects'
import { usePresets } from '../composables/usePresets'
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '../config/constants'
import { showSuccess, showError, showWarning } from '../utils/toast'

const props = defineProps({
  modelValue: Boolean,
  project: Object
})

const emit = defineEmits(['update:modelValue', 'saved'])

const toast = useToast()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const editingProject = computed(() => props.project)

// Use composables
const { createProject, updateProject } = useProjects()
const { 
  presets,
  categories,
  loading: loadingPresets,
  selectedCategory,
  selectedPreset,
  presetDetails,
  filteredPresets,
  presetComposeContent,
  loadPresets,
  selectCategory,
  selectPreset: selectPresetFn,
  resetSelection
} = usePresets()

const saving = ref(false)

// Form data
const formData = ref({
  name: '',
  domain: '',
  compose_content: '',
  env_vars: {}
})

// Computed
const canSave = computed(() => {
  if (editingProject.value) {
    return !!(formData.value.name && formData.value.domain && formData.value.compose_content)
  }
  return !!(formData.value.name && formData.value.domain && 
         (selectedPreset.value || formData.value.compose_content))
})

// Methods  
const selectPreset = async (presetId) => {
  try {
    const preset = await selectPresetFn(presetId)
    // Auto-fill env vars
    formData.value.env_vars = preset.default_env_vars || {}
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.LOAD_PRESETS_FAILED)
  }
}

const resetForm = () => {
  formData.value = {
    name: '',
    domain: '',
    compose_content: '',
    env_vars: {}
  }
  resetSelection()
}

const handleSave = async () => {
  // Validation
  if (!formData.value.name || !formData.value.domain) {
    showWarning(toast, ERROR_MESSAGES.VALIDATION_ERROR)
    return
  }

  // Use preset content if selected, otherwise use custom
  const composeContent = presetDetails.value?.compose_content || formData.value.compose_content
  
  if (!composeContent) {
    showWarning(toast, 'Please select a preset or provide docker-compose content')
    return
  }

  saving.value = true
  try {
    const projectData = {
      ...formData.value,
      compose_content: composeContent
    }
    
    if (editingProject.value) {
      await updateProject(editingProject.value.id, projectData)
      showSuccess(toast, SUCCESS_MESSAGES.PROJECT_UPDATED)
    } else {
      await createProject(projectData)
      showSuccess(toast, SUCCESS_MESSAGES.PROJECT_CREATED)
    }
    
    emit('saved')
    handleClose()
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.SAVE_PROJECT_FAILED)
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

// Watch for dialog opening
watch(visible, (newVal) => {
  if (newVal) {
    if (editingProject.value) {
      // Load project data
      formData.value = {
        name: editingProject.value.name,
        domain: editingProject.value.domain,
        compose_content: editingProject.value.compose_content,
        env_vars: editingProject.value.env_vars || {}
      }
    } else {
      // Load presets for new project
      if (presets.value.length === 0) {
        loadPresets()
      }
      resetForm()
    }
  }
})
</script>

<style scoped>
.form-section {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.form-section h3 {
  margin-top: 0;
  color: #495057;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.w-full {
  width: 100%;
}

/* Categories */
.categories-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.category-chip {
  cursor: pointer;
  transition: all 0.2s;
}

.category-chip:hover {
  background: #e3f2fd !important;
}

.selected-category {
  background: #2196f3 !important;
  color: white !important;
}

/* Presets Grid */
.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  max-height: 500px;
  overflow-y: auto;
  padding: 0.5rem;
}

.preset-card {
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.preset-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.selected-preset {
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.preset-icon {
  font-size: 3rem;
  text-align: center;
  padding: 1rem;
}

.preset-description {
  font-size: 0.875rem;
  color: #666;
  margin: 0 0 1rem 0;
  min-height: 40px;
}

.preset-tags {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.preset-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.presets-loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.preset-skeleton {
  border-radius: 8px;
}

/* Preview */
.preview-section {
  margin-top: 1.5rem;
}

.preview-section h3 {
  margin-bottom: 0.5rem;
  color: #495057;
}
</style>

