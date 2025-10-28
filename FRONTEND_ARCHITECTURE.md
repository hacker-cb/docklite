# Frontend Architecture - Vue 3 Best Practices

**Date**: 2025-10-28  
**Status**: ✅ Complete

## Overview

DockLite frontend follows Vue 3 Composition API best practices with proper separation of concerns, reusable composables, and clean component architecture.

## Directory Structure

```
frontend/src/
├── components/              # Reusable UI components
│   ├── CreateProjectDialog.vue
│   ├── EnvVarsDialog.vue
│   └── DeployInfoDialog.vue
│
├── views/                   # Route-level components
│   ├── ProjectsView.vue
│   └── UsersView.vue
│
├── composables/             # Reusable composition functions
│   ├── useProjects.js
│   ├── useContainers.js
│   └── usePresets.js
│
├── config/                  # Application constants
│   └── constants.js
│
├── utils/                   # Utility functions
│   ├── formatters.js
│   └── toast.js
│
├── App.vue                  # Root component (auth + layout)
├── Login.vue                # Login form
├── Setup.vue                # Initial setup form
├── router.js                # Vue Router configuration
├── api.js                   # API client (Axios)
└── main.js                  # Application entry point
```

## Architecture Principles

### 1. **Composables** (Composition API)

Composables extract and encapsulate reusable stateful logic following Vue 3 best practices.

**Why Composables?**
- ✅ Reusable across components
- ✅ Better code organization
- ✅ Easier to test
- ✅ Type-safe (when using TypeScript)

**Naming Convention:**
- Always start with `use` prefix
- Use camelCase: `useProjects`, `useContainers`

**Example:**

```javascript
// composables/useProjects.js
export function useProjects() {
  const projects = ref([])
  const loading = ref(false)
  
  const loadProjects = async () => { ... }
  
  return { projects, loading, loadProjects }
}

// In component
const { projects, loading, loadProjects } = useProjects()
```

### 2. **Constants** (Configuration)

All magic values are extracted to `config/constants.js` for maintainability.

**Benefits:**
- ✅ Single source of truth
- ✅ Easy to update
- ✅ No magic strings in code

**Example:**

```javascript
// config/constants.js
export const STATUS_SEVERITY = {
  created: 'info',
  running: 'success',
  stopped: 'warning',
  error: 'danger'
}

// In component
import { STATUS_SEVERITY } from '@/config/constants'
const severity = STATUS_SEVERITY[status]
```

### 3. **Utils** (Helper Functions)

Pure utility functions for common operations.

**Guidelines:**
- Pure functions (no side effects)
- Easy to test
- Well-documented

**Example:**

```javascript
// utils/formatters.js
export const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

// utils/toast.js
export const showSuccess = (toast, message) => {
  toast.add({
    severity: 'success',
    detail: message,
    life: 3000
  })
}
```

### 4. **Component Communication**

**Props Down, Events Up:**
```vue
<!-- Parent -->
<CreateProjectDialog 
  v-model="showDialog"
  :project="editingProject"
  @saved="handleSaved"
/>

<!-- Child -->
const props = defineProps({
  modelValue: Boolean,
  project: Object
})

const emit = defineEmits(['update:modelValue', 'saved'])
```

## Composables Reference

### useProjects()

**Purpose:** Manage project CRUD operations

**Returns:**
```javascript
{
  projects,          // ref<Array>
  loading,           // ref<boolean>
  error,             // ref<Error|null>
  loadProjects,      // () => Promise<Array>
  createProject,     // (data) => Promise<Object>
  updateProject,     // (id, data) => Promise<Object>
  deleteProject,     // (id) => Promise<void>
  getProject,        // (id) => Promise<Object>
  getEnvVars,        // (id) => Promise<Object>
  updateEnvVars      // (id, vars) => Promise<void>
}
```

**Usage:**
```javascript
const { projects, loading, loadProjects } = useProjects()

onMounted(() => {
  loadProjects()
})
```

### useContainers()

**Purpose:** Manage Docker container operations

**Returns:**
```javascript
{
  loading,              // ref<boolean>
  error,                // ref<Error|null>
  startContainer,       // (projectId) => Promise<Object>
  stopContainer,        // (projectId) => Promise<Object>
  restartContainer,     // (projectId) => Promise<Object>
  getContainerStatus    // (projectId) => Promise<Object>
}
```

**Usage:**
```javascript
const { startContainer, stopContainer } = useContainers()

const start = async (project) => {
  await startContainer(project.id)
  loadProjects() // Refresh list
}
```

### usePresets()

**Purpose:** Manage preset selection and loading

**Returns:**
```javascript
{
  presets,              // ref<Array>
  categories,           // ref<Array>
  loading,              // ref<boolean>
  error,                // ref<Error|null>
  selectedCategory,     // ref<string>
  selectedPreset,       // ref<Object|null>
  presetDetails,        // ref<Object|null>
  filteredPresets,      // computed<Array>
  presetComposeContent, // computed<string>
  loadPresets,          // () => Promise<void>
  selectCategory,       // (id) => void
  selectPreset,         // (id) => Promise<Object>
  resetSelection        // () => void
}
```

**Usage:**
```javascript
const { 
  presets, 
  loadPresets, 
  selectPreset,
  presetComposeContent 
} = usePresets()

onMounted(() => {
  loadPresets()
})
```

## Constants Reference

### STATUS_SEVERITY

Maps project status to PrimeVue Tag severity:

```javascript
{
  created: 'info',    // Blue
  running: 'success', // Green
  stopped: 'warning', // Orange
  error: 'danger'     // Red
}
```

### TOAST_DURATION

Standard toast notification durations:

```javascript
{
  SHORT: 2000,   // 2 seconds
  NORMAL: 3000,  // 3 seconds
  LONG: 5000     // 5 seconds
}
```

### ERROR_MESSAGES / SUCCESS_MESSAGES

Pre-defined messages for consistency:

```javascript
ERROR_MESSAGES.LOAD_PROJECTS_FAILED
SUCCESS_MESSAGES.PROJECT_CREATED
```

## Utils Reference

### formatters.js

**formatDate(dateString)**
- Converts ISO date to locale string
- Returns empty string for null/undefined

**formatError(error)**
- Parses Axios error to readable message
- Handles FastAPI 422 validation errors
- Returns user-friendly error text

### toast.js

**showSuccess(toast, message, summary?)**
- Shows success toast (green)
- Default duration: 3s

**showError(toast, error, summary?)**
- Shows error toast (red)
- Auto-formats error message
- Default duration: 5s

**showWarning(toast, message, summary?)**
- Shows warning toast (orange)
- Default duration: 3s

**showInfo(toast, message, summary?)**
- Shows info toast (blue)
- Default duration: 2s

## Component Patterns

### Typical View Component Structure

```vue
<template>
  <div class="view">
    <div class="toolbar">
      <h2>Title</h2>
      <Button @click="showDialog = true">Action</Button>
    </div>
    
    <DataTable :value="items" :loading="loading">
      <!-- columns -->
    </DataTable>
    
    <!-- Dialogs -->
    <SomeDialog v-model="showDialog" @saved="handleSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useItems } from '@/composables/useItems'
import { showSuccess, showError } from '@/utils/toast'
import SomeDialog from '@/components/SomeDialog.vue'

const toast = useToast()
const { items, loading, loadItems } = useItems()
const showDialog = ref(false)

const handleSaved = () => {
  showDialog.value = false
  loadItems()
}

onMounted(() => {
  loadItems()
})
</script>
```

### Typical Dialog Component Structure

```vue
<template>
  <Dialog v-model:visible="visible" header="Title">
    <!-- Form fields -->
    
    <template #footer>
      <Button label="Cancel" @click="handleClose" />
      <Button label="Save" @click="handleSave" :loading="saving" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useItems } from '@/composables/useItems'
import { showSuccess, showError } from '@/utils/toast'

const props = defineProps({
  modelValue: Boolean,
  item: Object
})

const emit = defineEmits(['update:modelValue', 'saved'])

const toast = useToast()
const { createItem, updateItem } = useItems()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const saving = ref(false)
const formData = ref({...})

const handleSave = async () => {
  saving.value = true
  try {
    if (props.item) {
      await updateItem(props.item.id, formData.value)
    } else {
      await createItem(formData.value)
    }
    emit('saved')
    handleClose()
  } catch (error) {
    showError(toast, error)
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
  formData.value = {...}
}
</script>
```

## Best Practices

### ✅ DO

1. **Use composables for reusable logic**
   ```javascript
   const { items, loading, loadItems } = useItems()
   ```

2. **Use constants for magic values**
   ```javascript
   import { STATUS_SEVERITY } from '@/config/constants'
   ```

3. **Use utils for common operations**
   ```javascript
   import { formatDate, showSuccess } from '@/utils'
   ```

4. **Keep components focused and small**
   - Components should do ONE thing
   - Extract complex logic to composables

5. **Use computed for derived state**
   ```javascript
   const filteredItems = computed(() => 
     items.value.filter(i => i.active)
   )
   ```

6. **Handle loading/error states**
   ```javascript
   const loading = ref(false)
   const error = ref(null)
   ```

### ❌ DON'T

1. **Don't duplicate logic across components**
   - Extract to composable instead

2. **Don't hardcode strings**
   - Use constants instead

3. **Don't write inline error handlers**
   - Use toast utils instead

4. **Don't create huge monolithic components**
   - Break down into smaller components

5. **Don't access API directly in components**
   - Use composables as abstraction layer

## Testing Strategy

### Unit Tests (Composables)

```javascript
import { describe, it, expect } from 'vitest'
import { useProjects } from './useProjects'

describe('useProjects', () => {
  it('loads projects successfully', async () => {
    const { projects, loadProjects } = useProjects()
    await loadProjects()
    expect(projects.value).toHaveLength(> 0)
  })
})
```

### Component Tests

```javascript
import { mount } from '@vue/test-utils'
import ProjectsView from './ProjectsView.vue'

describe('ProjectsView', () => {
  it('renders projects table', () => {
    const wrapper = mount(ProjectsView)
    expect(wrapper.find('table').exists()).toBe(true)
  })
})
```

## Migration from Old Code

### Before (No composables):

```javascript
// ProjectsView.vue
const projects = ref([])
const loading = ref(false)

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await projectsApi.getAll()
    projects.value = response.data.projects
  } catch (error) {
    toast.add({ severity: 'error', detail: 'Failed' })
  } finally {
    loading.value = false
  }
}
```

### After (With composables):

```javascript
// ProjectsView.vue
import { useProjects } from '@/composables/useProjects'
import { showError } from '@/utils/toast'

const { projects, loading, loadProjects } = useProjects()

// Just call it - error handling is in composable
try {
  await loadProjects()
} catch (error) {
  showError(toast, error)
}
```

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| Lines in components | 200-300 | 100-150 |
| Code reusability | Low | High |
| Testing | Difficult | Easy |
| Maintenance | Hard | Easy |
| Type safety | Poor | Good |
| Consistency | Low | High |

## Future Improvements

1. **TypeScript** - Add type definitions
2. **Pinia** - State management for complex state
3. **Vitest** - Comprehensive test coverage
4. **Storybook** - Component documentation
5. **i18n** - Internationalization support

## Conclusion

✅ **Vue 3 Best Practices Applied!**

- Composables for logic reuse
- Constants for configuration
- Utils for common operations
- Clean component structure
- Proper error handling
- Consistent patterns

**Result:** Maintainable, testable, scalable frontend! 🚀

