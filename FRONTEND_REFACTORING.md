# Frontend Refactoring - Component Structure

**Date**: 2025-10-28

## Summary

Refactored frontend to follow proper Vue.js component-based architecture. Reduced App.vue from 983 lines to 194 lines by extracting reusable dialog components.

## New Component Structure

```
frontend/src/
├── App.vue (194 lines, was 983)  # Main app with auth only
├── Login.vue                       # Login form
├── Setup.vue                       # Initial setup form
├── router.js                       # Vue Router config
├── api.js                          # API client
├── main.js                         # App entry point
├── components/                     # 🆕 Reusable components
│   ├── CreateProjectDialog.vue    # Create/edit project with presets
│   ├── EnvVarsDialog.vue          # Environment variables management
│   └── DeployInfoDialog.vue       # Deployment instructions
└── views/                          # Route views
    ├── ProjectsView.vue           # Projects list with actions
    └── UsersView.vue              # User management (admin only)
```

## Components Overview

### 1. App.vue (194 lines) ✅
**Responsibilities:**
- Authentication flow (setup/login/logout)
- Header with user info
- Navigation tabs (Projects/Users)
- Router view

**What was removed:**
- All project CRUD logic → ProjectsView.vue
- All dialog components → components/
- Presets logic → CreateProjectDialog.vue
- 789 lines of code!

**Props/Events:** None (root component)

### 2. CreateProjectDialog.vue (467 lines) 🆕
**Responsibilities:**
- Create/edit project form
- Preset selection with categories
- Docker compose preview
- Form validation

**Props:**
- `modelValue: Boolean` - Dialog visibility
- `project: Object` - Project to edit (null for create)

**Events:**
- `update:modelValue` - Close dialog
- `saved` - Project saved successfully

**Usage:**
```vue
<CreateProjectDialog 
  v-model="showDialog" 
  :project="editingProject"
  @saved="handleSaved"
/>
```

### 3. EnvVarsDialog.vue (137 lines) 🆕
**Responsibilities:**
- Display/edit environment variables
- Add/remove variables
- Save to backend

**Props:**
- `modelValue: Boolean` - Dialog visibility
- `projectId: Number` - Project ID to load env vars

**Events:**
- `update:modelValue` - Close dialog
- `saved` - Env vars saved successfully

**Usage:**
```vue
<EnvVarsDialog 
  v-model="showDialog" 
  :project-id="projectId"
  @saved="loadProjects"
/>
```

### 4. DeployInfoDialog.vue (113 lines) 🆕
**Responsibilities:**
- Display deployment instructions
- Show SSH commands
- Deploy script template

**Props:**
- `modelValue: Boolean` - Dialog visibility
- `projectId: Number` - Project ID to load deploy info

**Events:**
- `update:modelValue` - Close dialog

**Usage:**
```vue
<DeployInfoDialog 
  v-model="showDialog" 
  :project-id="projectId"
/>
```

### 5. ProjectsView.vue (263 lines)
**Responsibilities:**
- Projects table with actions
- Container management (start/stop/restart)
- Delete confirmation
- Import and use dialog components

**State:**
- Projects list
- Dialog visibility flags
- Selected project IDs for dialogs

### 6. UsersView.vue (435 lines)
**Responsibilities:**
- Users table (admin only)
- Create/edit/delete users
- Change password
- Toggle admin/active status

## Benefits of Refactoring

### 1. **Maintainability** ✅
- Each component has single responsibility
- Easy to find and modify specific features
- Reduced cognitive load

### 2. **Reusability** ✅
- Dialogs can be used from any view
- Components are self-contained
- Easy to test in isolation

### 3. **Code Organization** ✅
- Clear separation of concerns
- Logical file structure
- Easier onboarding for new developers

### 4. **Performance** ✅
- Lazy loading of dialog components
- Better Vue reactivity optimization
- Smaller bundle chunks

## Communication Pattern

### Parent → Child (Props)
```vue
<!-- Parent -->
<CreateProjectDialog 
  v-model="showDialog" 
  :project="editingProject"
/>

<!-- Child receives via defineProps -->
const props = defineProps({
  modelValue: Boolean,
  project: Object
})
```

### Child → Parent (Events)
```vue
<!-- Child emits events -->
const emit = defineEmits(['update:modelValue', 'saved'])
emit('saved')

<!-- Parent handles events -->
<CreateProjectDialog 
  @saved="handleProjectSaved"
/>
```

### v-model (Two-way binding)
```vue
<!-- Syntactic sugar for -->
<Dialog v-model:visible="showDialog" />

<!-- Equivalent to -->
<Dialog 
  :visible="showDialog" 
  @update:visible="showDialog = $event"
/>
```

## Migration Checklist

- [x] Create `components/` directory
- [x] Extract CreateProjectDialog component
- [x] Extract EnvVarsDialog component
- [x] Extract DeployInfoDialog component
- [x] Update ProjectsView to use new components
- [x] Clean up App.vue (remove all dialog code)
- [x] Remove unused state/methods from App.vue
- [x] Remove unused styles from App.vue
- [x] Test all dialogs work correctly
- [x] Verify no regressions

## Files Changed

**New Files:**
- ✅ `frontend/src/components/CreateProjectDialog.vue`
- ✅ `frontend/src/components/EnvVarsDialog.vue`
- ✅ `frontend/src/components/DeployInfoDialog.vue`

**Modified Files:**
- ✅ `frontend/src/App.vue` (983 → 194 lines, -789!)
- ✅ `frontend/src/views/ProjectsView.vue` (updated to use components)

## Best Practices Applied

1. **Single Responsibility Principle**
   - Each component does ONE thing well

2. **Component Composition**
   - Small, focused components
   - Compose into larger views

3. **Props Down, Events Up**
   - Data flows down via props
   - Events bubble up to parents

4. **Self-Contained Components**
   - Components manage their own state
   - Load their own data
   - Handle their own errors

5. **Consistent Naming**
   - Components use PascalCase
   - Events use kebab-case
   - Clear, descriptive names

## Testing Strategy

### Component Testing
```javascript
// Test CreateProjectDialog
- Opens with empty form for create
- Loads project data for edit
- Validates required fields
- Submits correctly
- Emits events properly

// Test EnvVarsDialog
- Loads env vars on open
- Adds new variables
- Deletes variables
- Saves to backend

// Test DeployInfoDialog
- Loads deploy info on open
- Displays all commands
- Handles errors gracefully
```

## Future Improvements

1. **Extract more components:**
   - PresetSelector (from CreateProjectDialog)
   - EnvVarsList (from EnvVarsDialog)
   - ProjectActions (action buttons)

2. **Add composables:**
   - `useProjectDialog()` - Dialog state management
   - `useProjects()` - Projects CRUD logic
   - `useToast()` - Already using PrimeVue's

3. **TypeScript:**
   - Add type definitions
   - Better IDE support
   - Catch errors at compile time

4. **Storybook:**
   - Document components visually
   - Test in isolation
   - Design system

## Conclusion

✅ **Refactoring Complete!**

Frontend now follows Vue.js best practices with:
- Clear component hierarchy
- Separation of concerns
- Reusable dialog components
- Much cleaner codebase

**Before:** 983-line monolithic App.vue  
**After:** 194-line App.vue + 3 focused dialog components

**Savings:** 789 lines removed from App.vue! 🎉

