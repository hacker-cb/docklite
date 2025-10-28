<template>
  <Dialog 
    v-model:visible="visible" 
    header="Environment Variables"
    :modal="true"
    :style="{ width: '600px' }"
    @hide="handleClose"
  >
    <div class="env-list">
      <div v-for="(value, key) in localEnvVars" :key="key" class="env-item">
        <div class="env-key">{{ key }}</div>
        <InputText v-model="localEnvVars[key]" class="env-value" />
        <Button 
          icon="pi pi-times" 
          class="p-button-rounded p-button-text p-button-danger p-button-sm" 
          @click="deleteEnvVar(key)"
        />
      </div>
    </div>
    
    <div class="env-add">
      <InputText v-model="newEnvKey" placeholder="Key" class="env-add-key" @keyup.enter="addEnvVar" />
      <InputText v-model="newEnvValue" placeholder="Value" class="env-add-value" @keyup.enter="addEnvVar" />
      <Button icon="pi pi-plus" @click="addEnvVar" class="p-button-sm" />
    </div>

    <template #footer>
      <Button 
        label="Cancel" 
        icon="pi pi-times" 
        @click="handleClose" 
        class="p-button-text"
      />
      <Button 
        label="Save" 
        icon="pi pi-check" 
        @click="handleSave"
        :loading="saving"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { projectsApi } from '../api'

const props = defineProps({
  modelValue: Boolean,
  projectId: Number
})

const emit = defineEmits(['update:modelValue', 'saved'])

const toast = useToast()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const localEnvVars = ref({})
const newEnvKey = ref('')
const newEnvValue = ref('')
const saving = ref(false)

const addEnvVar = () => {
  if (newEnvKey.value && newEnvValue.value) {
    localEnvVars.value[newEnvKey.value] = newEnvValue.value
    newEnvKey.value = ''
    newEnvValue.value = ''
  }
}

const deleteEnvVar = (key) => {
  delete localEnvVars.value[key]
}

const handleSave = async () => {
  if (!props.projectId) return

  saving.value = true
  try {
    await projectsApi.updateEnv(props.projectId, localEnvVars.value)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Environment variables updated successfully',
      life: 3000
    })
    emit('saved')
    handleClose()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update environment variables',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
  localEnvVars.value = {}
  newEnvKey.value = ''
  newEnvValue.value = ''
}

const loadEnvVars = async () => {
  if (!props.projectId) return
  
  try {
    const response = await projectsApi.getEnv(props.projectId)
    localEnvVars.value = response.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load environment variables',
      life: 3000
    })
  }
}

// Watch for dialog opening
watch(visible, (newVal) => {
  if (newVal && props.projectId) {
    loadEnvVars()
  }
})
</script>

<style scoped>
.env-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.env-item {
  display: grid;
  grid-template-columns: 120px 1fr auto;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.env-key {
  font-weight: 600;
  color: #495057;
  font-size: 0.875rem;
}

.env-value {
  width: 100%;
}

.env-add {
  display: grid;
  grid-template-columns: 120px 1fr auto;
  gap: 0.5rem;
  align-items: center;
  padding: 0.75rem;
  background: #e3f2fd;
  border-radius: 4px;
}

.env-add-key {
  width: 100%;
}

.env-add-value {
  width: 100%;
}
</style>

