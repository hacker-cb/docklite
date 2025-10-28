<template>
  <div class="users-container">
    <div class="toolbar">
      <h2><i class="pi pi-users"></i> Users</h2>
      <Button 
        label="Add User" 
        icon="pi pi-plus" 
        @click="showCreateDialog = true"
        class="p-button-success"
      />
    </div>

    <DataTable 
      :value="users" 
      :loading="loading"
      class="p-datatable-sm"
      stripedRows
    >
      <Column field="id" header="ID" style="width: 80px"></Column>
      <Column field="username" header="Username"></Column>
      <Column field="email" header="Email"></Column>
      <Column field="is_admin" header="Admin" style="width: 100px">
        <template #body="slotProps">
          <Tag 
            :value="slotProps.data.is_admin ? 'Admin' : 'User'" 
            :severity="slotProps.data.is_admin ? 'success' : 'info'"
          />
        </template>
      </Column>
      <Column field="is_active" header="Status" style="width: 100px">
        <template #body="slotProps">
          <Tag 
            :value="slotProps.data.is_active ? 'Active' : 'Inactive'" 
            :severity="slotProps.data.is_active ? 'success' : 'danger'"
          />
        </template>
      </Column>
      <Column field="created_at" header="Created" style="width: 180px">
        <template #body="slotProps">
          {{ formatDate(slotProps.data.created_at) }}
        </template>
      </Column>
      <Column header="Actions" style="width: 200px">
        <template #body="slotProps">
          <Button 
            icon="pi pi-key" 
            class="p-button-rounded p-button-text p-button-warning" 
            @click="showChangePassword(slotProps.data)"
            v-tooltip="'Change Password'"
          />
          <Button 
            :icon="slotProps.data.is_active ? 'pi pi-ban' : 'pi pi-check'" 
            class="p-button-rounded p-button-text" 
            @click="toggleActive(slotProps.data)"
            v-tooltip="slotProps.data.is_active ? 'Deactivate' : 'Activate'"
          />
          <Button 
            :icon="slotProps.data.is_admin ? 'pi pi-user' : 'pi pi-shield'" 
            class="p-button-rounded p-button-text p-button-info" 
            @click="toggleAdmin(slotProps.data)"
            v-tooltip="slotProps.data.is_admin ? 'Remove Admin' : 'Make Admin'"
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

    <!-- Create User Dialog -->
    <Dialog 
      v-model:visible="showCreateDialog" 
      header="Create New User"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="form-group">
        <label>Username *</label>
        <InputText v-model="newUser.username" class="w-full" placeholder="username" />
      </div>

      <div class="form-group">
        <label>Email</label>
        <InputText v-model="newUser.email" type="email" class="w-full" placeholder="user@example.com (optional)" />
      </div>

      <div class="form-group">
        <label>Password *</label>
        <input 
          v-model="newUser.password" 
          type="password" 
          class="p-inputtext p-component w-full" 
          placeholder="Enter password"
          autocomplete="new-password"
        />
      </div>

      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 0.5rem;">
          <input type="checkbox" v-model="newUser.is_admin" />
          Make this user an administrator
        </label>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="closeCreateDialog" 
          class="p-button-text"
        />
        <Button 
          label="Create" 
          icon="pi pi-check" 
          @click="createUser"
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Change Password Dialog -->
    <Dialog 
      v-model:visible="showPasswordDialog" 
      header="Change Password"
      :modal="true"
      :style="{ width: '400px' }"
    >
      <div v-if="selectedUser">
        <p><strong>User:</strong> {{ selectedUser.username }}</p>
        
        <div class="form-group">
          <label>New Password *</label>
          <input 
            v-model="newPassword" 
            type="password" 
            class="p-inputtext p-component w-full" 
            placeholder="Enter new password"
            autocomplete="new-password"
          />
          <small class="form-hint">Minimum 6 characters</small>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="closePasswordDialog" 
          class="p-button-text"
        />
        <Button 
          label="Change Password" 
          icon="pi pi-check" 
          @click="changePassword"
          :loading="saving"
        />
      </template>
    </Dialog>

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { usersApi } from './api'

const toast = useToast()
const confirm = useConfirm()

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showPasswordDialog = ref(false)
const selectedUser = ref(null)
const newPassword = ref('')

const newUser = ref({
  username: '',
  email: '',
  password: '',
  is_admin: false
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await usersApi.getAll()
    users.value = response.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to load users',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const createUser = async () => {
  if (!newUser.value.username || !newUser.value.password) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Username and password are required',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    const userData = {
      username: newUser.value.username,
      email: newUser.value.email || null,
      password: newUser.value.password
    }
    
    await usersApi.create(userData)
    
    // If user is admin, update after creation
    if (newUser.value.is_admin) {
      const response = await usersApi.getAll()
      const createdUser = response.data.find(u => u.username === userData.username)
      if (createdUser) {
        await usersApi.update(createdUser.id, { is_admin: true })
      }
    }
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'User created successfully',
      life: 3000
    })
    closeCreateDialog()
    loadUsers()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to create user',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const toggleActive = async (user) => {
  try {
    await usersApi.update(user.id, { is_active: !user.is_active })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `User ${user.is_active ? 'deactivated' : 'activated'}`,
      life: 3000
    })
    loadUsers()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to update user',
      life: 3000
    })
  }
}

const toggleAdmin = async (user) => {
  try {
    await usersApi.update(user.id, { is_admin: !user.is_admin })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Admin rights ${user.is_admin ? 'removed' : 'granted'}`,
      life: 3000
    })
    loadUsers()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to update user',
      life: 3000
    })
  }
}

const showChangePassword = (user) => {
  selectedUser.value = user
  newPassword.value = ''
  showPasswordDialog.value = true
}

const changePassword = async () => {
  if (!newPassword.value || newPassword.value.length < 6) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Password must be at least 6 characters',
      life: 3000
    })
    return
  }

  saving.value = true
  try {
    await usersApi.changePassword(selectedUser.value.id, newPassword.value)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Password changed successfully',
      life: 3000
    })
    closePasswordDialog()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to change password',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const confirmDelete = (user) => {
  confirm.require({
    message: `Are you sure you want to delete user "${user.username}"?`,
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteUser(user.id)
  })
}

const deleteUser = async (id) => {
  try {
    await usersApi.delete(id)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'User deleted successfully',
      life: 3000
    })
    loadUsers()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Failed to delete user',
      life: 3000
    })
  }
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  newUser.value = {
    username: '',
    email: '',
    password: '',
    is_admin: false
  }
}

const closePasswordDialog = () => {
  showPasswordDialog.value = false
  selectedUser.value = null
  newPassword.value = ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
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
</style>

