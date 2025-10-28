<template>
  <div class="projects-view">
    <div class="toolbar">
      <Button 
        label="New Project" 
        icon="pi pi-plus" 
        @click="openCreateDialog"
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
      <Column header="Actions" style="width: 250px">
        <template #body="slotProps">
          <Button 
            icon="pi pi-upload" 
            class="p-button-rounded p-button-text p-button-info" 
            @click="showDeployInfo(slotProps.data)"
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
            @click="editEnvVars(slotProps.data)"
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

    <!-- All dialogs from App.vue will go here -->
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { projectsApi } from '../api'

const toast = useToast()
const confirm = useConfirm()

const projects = ref([])
const loading = ref(false)

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await projectsApi.getAll()
    projects.value = response.data.projects
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load projects',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  toast.add({
    severity: 'info',
    summary: 'Info',
    detail: 'Create project dialog - integrating...',
    life: 2000
  })
}

const showDeployInfo = (project) => {
  toast.add({
    severity: 'info',
    summary: 'Deploy Info',
    detail: `Project ID: ${project.id}`,
    life: 2000
  })
}

const editProject = (project) => {
  toast.add({
    severity: 'info',
    summary: 'Edit',
    detail: `Editing ${project.name}`,
    life: 2000
  })
}

const editEnvVars = (project) => {
  toast.add({
    severity: 'info',
    summary: 'Env Vars',
    detail: `Managing env for ${project.name}`,
    life: 2000
  })
}

const confirmDelete = (project) => {
  confirm.require({
    message: `Delete project "${project.name}"?`,
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteProject(project.id)
  })
}

const deleteProject = async (id) => {
  try {
    await projectsApi.delete(id)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Project deleted',
      life: 3000
    })
    loadProjects()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete project',
      life: 3000
    })
  }
}

const getStatusSeverity = (status) => {
  const map = {
    'created': 'info',
    'running': 'success',
    'stopped': 'warning',
    'error': 'danger'
  }
  return map[status] || 'info'
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.projects-view {
  padding: 0;
}

.toolbar {
  margin-bottom: 1rem;
}
</style>

