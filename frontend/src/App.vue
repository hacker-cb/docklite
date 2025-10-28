<template>
  <div class="app">
    <!-- Setup screen (first time) -->
    <Setup v-if="needsSetup && !isAuthenticated" @setup-complete="handleLoginSuccess" />

    <!-- Login screen -->
    <Login v-else-if="!isAuthenticated" @login-success="handleLoginSuccess" />

    <!-- Main app (authenticated) -->
    <div v-else>
      <header class="header">
        <div class="header-content">
          <div class="header-left">
            <h1><i class="pi pi-server"></i> DockLite</h1>
            <p>Web Server Management System</p>
          </div>
          <div class="header-right">
            <span class="user-info">
              <i class="pi pi-user"></i>
              {{ currentUser?.username }}
            </span>
            <Button 
              label="Logout" 
              icon="pi pi-sign-out" 
              @click="handleLogout"
              class="p-button-sm p-button-outlined"
            />
          </div>
        </div>
      </header>

      <main class="main-content">
      <!-- Navigation Tabs -->
      <div class="nav-tabs">
        <Button 
          :label="currentView === 'projects' ? 'Projects' : 'Projects'"
          icon="pi pi-server" 
          @click="currentView = 'projects'"
          :class="currentView === 'projects' ? 'p-button-primary' : 'p-button-outlined'"
        />
        <Button 
          v-if="currentUser?.is_admin"
          :label="currentView === 'users' ? 'Users' : 'Users'"
          icon="pi pi-users" 
          @click="currentView = 'users'"
          :class="currentView === 'users' ? 'p-button-primary' : 'p-button-outlined'"
        />
      </div>

      <!-- Projects View -->
      <div v-if="currentView === 'projects'">
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
      </div>

      <!-- Users View -->
      <Users v-if="currentView === 'users' && currentUser?.is_admin" />
    </main>
    </div>

    <!-- Create/Edit Project Dialog with Presets -->
    <Dialog 
      v-model:visible="showCreateDialog" 
      :header="editingProject ? 'Edit Project' : 'Create New Project'"
      :modal="true"
      :style="{ width: '900px' }"
      :maximizable="true"
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
          <small class="form-hint">Проект будет доступен через virtual host по этому домену</small>
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
          @click="closeDialog" 
          class="p-button-text"
        />
        <Button 
          :label="editingProject ? 'Update' : 'Create'" 
          icon="pi pi-check" 
          @click="saveProject"
          :loading="saving"
          :disabled="!canSave"
        />
      </template>
    </Dialog>

    <!-- Environment Variables Dialog -->
    <Dialog 
      v-model:visible="showEnvDialog" 
      header="Environment Variables"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div class="env-list">
        <div v-for="(value, key) in envVars" :key="key" class="env-item">
          <div class="env-key">{{ key }}</div>
          <InputText v-model="envVars[key]" class="env-value" />
          <Button 
            icon="pi pi-times" 
            class="p-button-rounded p-button-text p-button-danger p-button-sm" 
            @click="deleteEnvVar(key)"
          />
        </div>
      </div>
      
      <div class="env-add">
        <InputText v-model="newEnvKey" placeholder="Key" class="env-add-key" />
        <InputText v-model="newEnvValue" placeholder="Value" class="env-add-value" />
        <Button icon="pi pi-plus" @click="addEnvVar" class="p-button-sm" />
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="closeEnvDialog" 
          class="p-button-text"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          @click="saveEnvVars"
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Deployment Info Dialog -->
    <Dialog 
      v-model:visible="showDeployDialog" 
      header="Deployment Instructions"
      :modal="true"
      :style="{ width: '700px' }"
      :maximizable="true"
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
          @click="closeDeployDialog" 
          class="p-button-text"
        />
      </template>
    </Dialog>

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { projectsApi, presetsApi, deploymentApi, authApi } from './api'
import Login from './Login.vue'
import Setup from './Setup.vue'
import Users from './Users.vue'

const toast = useToast()
const confirm = useConfirm()

// Auth state
const isAuthenticated = ref(false)
const currentUser = ref(null)
const needsSetup = ref(false)

// Navigation
const currentView = ref('projects')  // 'projects' or 'users'

// State
const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showEnvDialog = ref(false)
const showDeployDialog = ref(false)
const editingProject = ref(null)
const currentProjectForEnv = ref(null)
const deployInfo = ref(null)

// Presets state
const presets = ref([])
const categories = ref([])
const loadingPresets = ref(false)
const selectedCategory = ref('all')
const selectedPreset = ref(null)
const presetDetails = ref(null)

// Form data
const formData = ref({
  name: '',
  domain: '',
  compose_content: '',
  env_vars: {}
})

const envVars = ref({})
const newEnvKey = ref('')
const newEnvValue = ref('')

// Computed
const filteredPresets = computed(() => {
  if (selectedCategory.value === 'all') {
    return presets.value
  }
  return presets.value.filter(p => p.category === selectedCategory.value)
})

const presetComposeContent = computed(() => {
  return presetDetails.value?.compose_content || ''
})

const canSave = computed(() => {
  if (editingProject.value) {
    return formData.value.name && formData.value.domain && formData.value.compose_content
  }
  // For new project: need name, domain, and either preset or custom compose
  return formData.value.name && formData.value.domain && 
         (selectedPreset.value || formData.value.compose_content)
})

// Methods
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

const loadPresets = async () => {
  loadingPresets.value = true
  try {
    const [presetsRes, categoriesRes] = await Promise.all([
      presetsApi.getAll(),
      presetsApi.getCategories()
    ])
    presets.value = presetsRes.data
    categories.value = categoriesRes.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load presets',
      life: 3000
    })
  } finally {
    loadingPresets.value = false
  }
}

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

const selectPreset = async (presetId) => {
  try {
    const response = await presetsApi.getById(presetId)
    presetDetails.value = response.data
    selectedPreset.value = presets.value.find(p => p.id === presetId)
    
    // Auto-fill env vars
    formData.value.env_vars = presetDetails.value.default_env_vars || {}
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load preset details',
      life: 3000
    })
  }
}

const openCreateDialog = () => {
  resetForm()
  showCreateDialog.value = true
  if (presets.value.length === 0) {
    loadPresets()
  }
}

const resetForm = () => {
  formData.value = {
    name: '',
    domain: '',
    compose_content: '',
    env_vars: {}
  }
  selectedPreset.value = null
  presetDetails.value = null
  selectedCategory.value = 'all'
}

const saveProject = async () => {
  if (!formData.value.name || !formData.value.domain) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please fill all required fields',
      life: 3000
    })
    return
  }

  // Use preset content if selected, otherwise use custom
  const composeContent = presetDetails.value?.compose_content || formData.value.compose_content
  
  if (!composeContent) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please select a preset or provide docker-compose content',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    const projectData = {
      ...formData.value,
      compose_content: composeContent
    }
    
    if (editingProject.value) {
      await projectsApi.update(editingProject.value.id, projectData)
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Project updated successfully',
        life: 3000
      })
    } else {
      await projectsApi.create(projectData)
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Project created successfully',
        life: 3000
      })
    }
    closeDialog()
    loadProjects()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to save project',
      life: 5000
    })
  } finally {
    saving.value = false
  }
}

const editProject = (project) => {
  editingProject.value = project
  formData.value = {
    name: project.name,
    domain: project.domain,
    compose_content: project.compose_content,
    env_vars: project.env_vars || {}
  }
  showCreateDialog.value = true
}

const confirmDelete = (project) => {
  confirm.require({
    message: `Are you sure you want to delete project "${project.name}"?`,
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
      detail: 'Project deleted successfully',
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

const editEnvVars = async (project) => {
  currentProjectForEnv.value = project
  try {
    const response = await projectsApi.getEnv(project.id)
    envVars.value = response.data
    showEnvDialog.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load environment variables',
      life: 3000
    })
  }
}

const addEnvVar = () => {
  if (newEnvKey.value && newEnvValue.value) {
    envVars.value[newEnvKey.value] = newEnvValue.value
    newEnvKey.value = ''
    newEnvValue.value = ''
  }
}

const deleteEnvVar = (key) => {
  delete envVars.value[key]
}

const saveEnvVars = async () => {
  if (!currentProjectForEnv.value) return

  saving.value = true
  try {
    await projectsApi.updateEnv(currentProjectForEnv.value.id, envVars.value)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Environment variables updated successfully',
      life: 3000
    })
    closeEnvDialog()
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

const closeDialog = () => {
  showCreateDialog.value = false
  editingProject.value = null
  resetForm()
}

const closeEnvDialog = () => {
  showEnvDialog.value = false
  currentProjectForEnv.value = null
  envVars.value = {}
  newEnvKey.value = ''
  newEnvValue.value = ''
}

const showDeployInfo = async (project) => {
  try {
    const response = await deploymentApi.getInfo(project.id)
    deployInfo.value = response.data
    showDeployDialog.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load deployment info',
      life: 3000
    })
  }
}

const closeDeployDialog = () => {
  showDeployDialog.value = false
  deployInfo.value = null
}

const getStatusSeverity = (status) => {
  const severityMap = {
    'created': 'info',
    'running': 'success',
    'stopped': 'warning',
    'error': 'danger'
  }
  return severityMap[status] || 'info'
}

const checkSetup = async () => {
  try {
    const response = await authApi.checkSetup()
    needsSetup.value = response.data.setup_needed
  } catch (error) {
    console.error('Failed to check setup status:', error)
  }
}

const checkAuth = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    isAuthenticated.value = false
    await checkSetup()
    return
  }

  try {
    const response = await authApi.me()
    currentUser.value = response.data
    isAuthenticated.value = true
    needsSetup.value = false
    loadProjects()
  } catch (error) {
    // Token invalid, clear it
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    await checkSetup()
  }
}

const handleLoginSuccess = (user) => {
  currentUser.value = user
  isAuthenticated.value = true
  needsSetup.value = false
  loadProjects()
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (error) {
    // Ignore errors on logout
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    currentUser.value = null
    projects.value = []
  }
}

onMounted(() => {
  checkAuth()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f8f9fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left h1 {
  margin: 0;
  font-size: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-left p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-weight: 500;
}

.main-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.toolbar {
  margin-bottom: 1rem;
}

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

.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
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

/* Environment Variables */
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

/* Deployment Dialog */
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
