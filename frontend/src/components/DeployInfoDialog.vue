<template>
  <Dialog 
    v-model:visible="visible" 
    header="Deployment Instructions"
    :modal="true"
    :style="{ width: '700px' }"
    :maximizable="true"
    @hide="handleClose"
  >
    <div v-if="deployInfo">
      <div class="deploy-info-section">
        <h3>📋 Project Information</h3>
        <p><strong>Project ID:</strong> {{ deployInfo.project_id }}</p>
        <p><strong>Domain:</strong> {{ deployInfo.domain }}</p>
        <p><strong>Server Path:</strong> <code>{{ deployInfo.project_path }}</code></p>
      </div>

      <div class="deploy-info-section">
        <h3>🚀 Quick Deploy</h3>
        <p><strong>1. Upload files:</strong></p>
        <pre class="command-box">{{ deployInfo.instructions.upload_files }}</pre>
        
        <p><strong>2. Start containers:</strong></p>
        <pre class="command-box">{{ deployInfo.instructions.start_containers }}</pre>
      </div>

      <div class="deploy-info-section">
        <h3>📝 Deploy Script</h3>
        <p>Create <code>deploy.sh</code> in your project:</p>
        <pre class="command-box">{{ deployInfo.examples.deploy_script }}</pre>
        <p><small>Make executable: <code>chmod +x deploy.sh</code></small></p>
      </div>

      <div class="deploy-info-section">
        <h3>🔧 Useful Commands</h3>
        <p><strong>View logs:</strong></p>
        <pre class="command-box">{{ deployInfo.instructions.view_logs }}</pre>
        
        <p><strong>Restart:</strong></p>
        <pre class="command-box">{{ deployInfo.instructions.restart }}</pre>
        
        <p><strong>Stop:</strong></p>
        <pre class="command-box">{{ deployInfo.instructions.stop }}</pre>
      </div>
    </div>

    <template #footer>
      <Button 
        label="Close" 
        icon="pi pi-times" 
        @click="handleClose" 
        class="p-button-text"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { deploymentApi } from '../api'

const props = defineProps({
  modelValue: Boolean,
  projectId: Number
})

const emit = defineEmits(['update:modelValue'])

const toast = useToast()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const deployInfo = ref(null)

const handleClose = () => {
  visible.value = false
  deployInfo.value = null
}

const loadDeployInfo = async () => {
  if (!props.projectId) return
  
  try {
    const response = await deploymentApi.getInfo(props.projectId)
    deployInfo.value = response.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load deployment info',
      life: 3000
    })
  }
}

// Watch for dialog opening
watch(visible, (newVal) => {
  if (newVal && props.projectId) {
    loadDeployInfo()
  }
})
</script>

<style scoped>
.deploy-info-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.deploy-info-section:last-child {
  border-bottom: none;
}

.deploy-info-section h3 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  color: #495057;
  font-size: 1.1rem;
}

.deploy-info-section p {
  margin: 0.5rem 0;
}

.command-box {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.75rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0.5rem 0;
}

.deploy-info-section code {
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}
</style>

