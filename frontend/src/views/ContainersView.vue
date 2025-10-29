<template>
  <div class="containers-view">
    <div class="view-header">
      <h2><i class="pi pi-box"></i> Containers</h2>
      <div class="header-actions">
        <Button 
          label="Refresh" 
          icon="pi pi-refresh" 
          @click="loadContainers"
          :loading="loading"
          class="p-button-sm"
        />
        <Button 
          label="Show All" 
          v-if="!showAll"
          icon="pi pi-eye" 
          @click="toggleShowAll"
          class="p-button-sm p-button-outlined"
        />
        <Button 
          label="Running Only" 
          v-else
          icon="pi pi-eye-slash" 
          @click="toggleShowAll"
          class="p-button-sm p-button-outlined"
        />
      </div>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Filter:</label>
        <Button 
          :label="`All (${containers.length})`"
          :class="filter === 'all' ? 'p-button-sm' : 'p-button-sm p-button-outlined'"
          @click="filter = 'all'"
        />
        <Button 
          :label="`System (${systemContainers.length})`"
          :class="filter === 'system' ? 'p-button-sm' : 'p-button-sm p-button-outlined'"
          @click="filter = 'system'"
        />
        <Button 
          :label="`Projects (${projectContainers.length})`"
          :class="filter === 'projects' ? 'p-button-sm' : 'p-button-sm p-button-outlined'"
          @click="filter = 'projects'"
        />
      </div>
    </div>

    <DataTable 
      :value="filteredContainers" 
      :loading="loading"
      stripedRows
      class="containers-table"
      :rowClass="getRowClass"
    >
      <Column field="name" header="Name" :sortable="true">
        <template #body="slotProps">
          <div class="container-name">
            <i :class="getStatusIcon(slotProps.data.status)"></i>
            <strong>{{ slotProps.data.name }}</strong>
            <Tag 
              v-if="slotProps.data.is_system" 
              value="SYSTEM" 
              severity="info" 
              class="ml-2"
            />
          </div>
        </template>
      </Column>
      
      <Column field="image" header="Image" :sortable="true">
        <template #body="slotProps">
          <code class="image-name">{{ slotProps.data.image }}</code>
        </template>
      </Column>
      
      <Column field="status" header="Status" :sortable="true">
        <template #body="slotProps">
          <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
        </template>
      </Column>
      
      <Column field="project" header="Project" :sortable="true">
        <template #body="slotProps">
          <span v-if="slotProps.data.project">{{ slotProps.data.project }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </Column>
      
      <Column field="ports" header="Ports">
        <template #body="slotProps">
          <div v-if="slotProps.data.ports.length > 0" class="ports-list">
            <Tag 
              v-for="(port, idx) in slotProps.data.ports.slice(0, 2)" 
              :key="idx"
              :value="port"
              severity="secondary"
              class="port-tag"
            />
            <Tag 
              v-if="slotProps.data.ports.length > 2"
              :value="`+${slotProps.data.ports.length - 2}`"
              severity="secondary"
            />
          </div>
          <span v-else class="text-muted">-</span>
        </template>
      </Column>
      
      <Column header="Actions" :exportable="false">
        <template #body="slotProps">
          <div class="action-buttons">
            <Button 
              v-if="slotProps.data.status !== 'running'"
              icon="pi pi-play" 
              @click="startContainer(slotProps.data)"
              class="p-button-sm p-button-success p-button-text"
              v-tooltip.top="'Start'"
            />
            <Button 
              v-if="slotProps.data.status === 'running'"
              icon="pi pi-stop" 
              @click="stopContainer(slotProps.data)"
              class="p-button-sm p-button-danger p-button-text"
              v-tooltip.top="slotProps.data.is_system ? 'Cannot stop system container' : 'Stop'"
              :disabled="slotProps.data.is_system"
            />
            <Button 
              icon="pi pi-refresh" 
              @click="restartContainer(slotProps.data)"
              class="p-button-sm p-button-warning p-button-text"
              v-tooltip.top="slotProps.data.is_system ? 'Cannot restart system container' : 'Restart'"
              :disabled="slotProps.data.status !== 'running' || slotProps.data.is_system"
            />
            <Button 
              icon="pi pi-file" 
              @click="showLogs(slotProps.data)"
              class="p-button-sm p-button-info p-button-text"
              v-tooltip.top="'Logs'"
            />
            <Button 
              icon="pi pi-trash" 
              @click="confirmRemove(slotProps.data)"
              class="p-button-sm p-button-danger p-button-text"
              v-tooltip.top="slotProps.data.is_system ? 'Cannot remove system container' : 'Remove'"
              :disabled="slotProps.data.is_system"
            />
          </div>
        </template>
      </Column>
      
      <template #empty>
        <div class="empty-state">
          <i class="pi pi-inbox"></i>
          <p>No containers found</p>
        </div>
      </template>
    </DataTable>

    <!-- Logs Dialog -->
    <Dialog 
      v-model:visible="logsDialog" 
      :header="`Logs: ${selectedContainer?.name}`"
      :style="{ width: '80vw' }" 
      :modal="true"
      :maximizable="true"
    >
      <div class="logs-controls">
        <Button 
          label="Refresh" 
          icon="pi pi-refresh" 
          @click="refreshLogs"
          :loading="logsLoading"
          class="p-button-sm"
        />
        <div class="tail-selector">
          <label>Lines:</label>
          <Dropdown 
            v-model="logsTail" 
            :options="[50, 100, 200, 500, 1000]"
            @change="refreshLogs"
            class="p-inputtext-sm"
          />
        </div>
      </div>
      
      <div class="logs-container">
        <pre v-if="containerLogs">{{ containerLogs }}</pre>
        <div v-else class="empty-logs">
          <i class="pi pi-info-circle"></i>
          <p>No logs available</p>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { containersApi } from '../api'
import { showSuccess, showError } from '../utils/toast'

const toast = useToast()
const confirm = useConfirm()

const containers = ref([])
const loading = ref(false)
const showAll = ref(true)
const filter = ref('all')

// Logs dialog
const logsDialog = ref(false)
const selectedContainer = ref(null)
const containerLogs = ref('')
const logsLoading = ref(false)
const logsTail = ref(100)

// Computed
const systemContainers = computed(() => 
  containers.value.filter(c => c.is_system)
)

const projectContainers = computed(() => 
  containers.value.filter(c => !c.is_system && c.project)
)

const filteredContainers = computed(() => {
  if (filter.value === 'system') {
    return systemContainers.value
  } else if (filter.value === 'projects') {
    return projectContainers.value
  }
  return containers.value
})

// Methods
const loadContainers = async () => {
  loading.value = true
  try {
    const response = await containersApi.getAll(showAll.value)
    containers.value = response.data.containers || []
  } catch (error) {
    showError(toast, error)
  } finally {
    loading.value = false
  }
}

const toggleShowAll = () => {
  showAll.value = !showAll.value
  loadContainers()
}

const startContainer = async (container) => {
  try {
    await containersApi.start(container.id)
    showSuccess(toast, `Container '${container.name}' started`)
    await loadContainers()
  } catch (error) {
    showError(toast, error)
  }
}

const stopContainer = async (container) => {
  try {
    await containersApi.stop(container.id)
    showSuccess(toast, `Container '${container.name}' stopped`)
    await loadContainers()
  } catch (error) {
    showError(toast, error)
  }
}

const restartContainer = async (container) => {
  try {
    await containersApi.restart(container.id)
    showSuccess(toast, `Container '${container.name}' restarted`)
    await loadContainers()
  } catch (error) {
    showError(toast, error)
  }
}

const confirmRemove = (container) => {
  confirm.require({
    message: `Are you sure you want to remove container '${container.name}'?`,
    header: 'Confirm Remove',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => removeContainer(container)
  })
}

const removeContainer = async (container) => {
  try {
    const force = container.status === 'running'
    await containersApi.remove(container.id, force)
    showSuccess(toast, `Container '${container.name}' removed`)
    await loadContainers()
  } catch (error) {
    showError(toast, error)
  }
}

const showLogs = async (container) => {
  selectedContainer.value = container
  logsDialog.value = true
  await refreshLogs()
}

const refreshLogs = async () => {
  if (!selectedContainer.value) return
  
  logsLoading.value = true
  try {
    const response = await containersApi.getLogs(selectedContainer.value.id, logsTail.value)
    containerLogs.value = response.data.logs
  } catch (error) {
    showError(toast, error)
    containerLogs.value = ''
  } finally {
    logsLoading.value = false
  }
}

const getStatusIcon = (status) => {
  if (status === 'running') return 'pi pi-circle-fill text-green'
  if (status === 'exited') return 'pi pi-circle-fill text-red'
  if (status === 'paused') return 'pi pi-pause-circle text-orange'
  return 'pi pi-circle text-gray'
}

const getStatusSeverity = (status) => {
  if (status === 'running') return 'success'
  if (status === 'exited') return 'danger'
  if (status === 'paused') return 'warning'
  return 'secondary'
}

const getRowClass = (data) => {
  if (data.is_system) return 'system-row'
  return ''
}

onMounted(() => {
  loadContainers()
})
</script>

<style scoped>
.containers-view {
  padding: 1rem 0;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.filters {
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #666;
}

.containers-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.container-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.container-name strong {
  font-family: 'Courier New', monospace;
}

.text-green {
  color: #22c55e;
}

.text-red {
  color: #ef4444;
}

.text-orange {
  color: #f97316;
}

.text-gray {
  color: #9ca3af;
}

.text-muted {
  color: #999;
  font-style: italic;
}

.image-name {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #374151;
}

.ports-list {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.port-tag {
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.1rem;
}

:deep(.system-row) {
  background-color: #f9fafb !important;
}

/* Logs Dialog */
.logs-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.tail-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tail-selector label {
  font-weight: 600;
  color: #666;
}

.logs-container {
  background: #1e1e1e;
  border-radius: 4px;
  padding: 1rem;
  max-height: 500px;
  overflow-y: auto;
}

.logs-container pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.empty-logs {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}

.empty-logs i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}
</style>



