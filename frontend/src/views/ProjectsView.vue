<template>
  <div class="projects-view">
    <div class="toolbar">
      <h2><i class="pi pi-folder"></i> Projects</h2>
      <Button 
        label="New Project" 
        icon="pi pi-plus" 
        @click="showCreateDialog = true"
        class="p-button-success"
      />
    </div>

    <DataTable 
      :value="projects" 
      :loading="loading"
      class="p-datatable-sm"
      stripedRows
      responsiveLayout="scroll"
    >
      <Column field="id" header="ID" style="width: 80px"></Column>
      <Column field="name" header="Name"></Column>
      <Column field="domain" header="Domain"></Column>
      <Column field="status" header="Status" style="width: 120px">
        <template #body="slotProps">
          <Tag 
            :value="slotProps.data.status" 
            :severity="getStatusSeverity(slotProps.data.status)"
          />
        </template>
      </Column>
      <Column header="Actions" style="width: 350px">
        <template #body="slotProps">
          <Button 
            icon="pi pi-play" 
            class="p-button-rounded p-button-text p-button-success" 
            @click="startContainer(slotProps.data)"
            v-tooltip="'Start'"
            :disabled="slotProps.data.status === 'running'"
          />
          <Button 
            icon="pi pi-stop" 
            class="p-button-rounded p-button-text p-button-warning" 
            @click="stopContainer(slotProps.data)"
            v-tooltip="'Stop'"
            :disabled="slotProps.data.status === 'stopped'"
          />
          <Button 
            icon="pi pi-refresh" 
            class="p-button-rounded p-button-text p-button-info" 
            @click="restartContainer(slotProps.data)"
            v-tooltip="'Restart'"
          />
          <Button 
            icon="pi pi-upload" 
            class="p-button-rounded p-button-text p-button-info" 
            @click="showDeployInfoDialog(slotProps.data)"
            v-tooltip="'Deploy Info'"
          />
          <Button 
            icon="pi pi-pencil" 
            class="p-button-rounded p-button-text" 
            @click="editProject(slotProps.data)"
            v-tooltip="'Edit'"
          />
          <Button 
            icon="pi pi-cog" 
            class="p-button-rounded p-button-text" 
            @click="editEnvVarsDialog(slotProps.data)"
            v-tooltip="'Environment Variables'"
          />
          <Button 
            icon="pi pi-trash" 
            class="p-button-rounded p-button-text p-button-danger" 
            @click="confirmDelete(slotProps.data)"
            v-tooltip="'Delete'"
          />
        </template>
      </Column>
    </DataTable>

    <!-- Dialogs -->
    <CreateProjectDialog 
      v-model="showCreateDialog" 
      :project="editingProject"
      @saved="handleProjectSaved"
    />
    
    <EnvVarsDialog 
      v-model="showEnvDialog" 
      :project-id="envProjectId"
      @saved="loadProjects"
    />
    
    <DeployInfoDialog 
      v-model="showDeployDialog" 
      :project-id="deployProjectId"
    />

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useProjects } from '../composables/useProjects'
import { useContainers } from '../composables/useContainers'
import { STATUS_SEVERITY, SUCCESS_MESSAGES, ERROR_MESSAGES } from '../config/constants'
import { showSuccess, showError } from '../utils/toast'
import CreateProjectDialog from '../components/CreateProjectDialog.vue'
import EnvVarsDialog from '../components/EnvVarsDialog.vue'
import DeployInfoDialog from '../components/DeployInfoDialog.vue'

const toast = useToast()
const confirm = useConfirm()

// Use composables
const { projects, loading, loadProjects } = useProjects()
const { 
  startContainer: startContainerFn, 
  stopContainer: stopContainerFn, 
  restartContainer: restartContainerFn 
} = useContainers()

// Dialog state
const showCreateDialog = ref(false)
const showEnvDialog = ref(false)
const showDeployDialog = ref(false)
const editingProject = ref(null)
const envProjectId = ref(null)
const deployProjectId = ref(null)

const editProject = (project) => {
  editingProject.value = project
  showCreateDialog.value = true
}

const showDeployInfoDialog = (project) => {
  deployProjectId.value = project.id
  showDeployDialog.value = true
}

const editEnvVarsDialog = (project) => {
  envProjectId.value = project.id
  showEnvDialog.value = true
}

const handleProjectSaved = () => {
  editingProject.value = null
  loadProjects()
}

const confirmDelete = (project) => {
  confirm.require({
    message: `Delete project "${project.name}"?`,
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteProject(project)
  })
}

const deleteProject = async (project) => {
  try {
    const { deleteProject: deleteProjectFn } = useProjects()
    await deleteProjectFn(project.id)
    showSuccess(toast, SUCCESS_MESSAGES.PROJECT_DELETED)
    await loadProjects()
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.DELETE_PROJECT_FAILED)
  }
}

const startContainer = async (project) => {
  try {
    await startContainerFn(project.id)
    showSuccess(toast, `${SUCCESS_MESSAGES.CONTAINER_STARTED} for "${project.name}"`)
    await loadProjects()
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.START_CONTAINER_FAILED)
  }
}

const stopContainer = async (project) => {
  try {
    await stopContainerFn(project.id)
    showSuccess(toast, `${SUCCESS_MESSAGES.CONTAINER_STOPPED} for "${project.name}"`)
    await loadProjects()
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.STOP_CONTAINER_FAILED)
  }
}

const restartContainer = async (project) => {
  try {
    await restartContainerFn(project.id)
    showSuccess(toast, `${SUCCESS_MESSAGES.CONTAINER_RESTARTED} for "${project.name}"`)
    await loadProjects()
  } catch (error) {
    showError(toast, error, ERROR_MESSAGES.RESTART_CONTAINER_FAILED)
  }
}

const getStatusSeverity = (status) => {
  return STATUS_SEVERITY[status] || 'info'
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.projects-view {
  padding: 1rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.toolbar h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #495057;
}
</style>

