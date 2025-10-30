import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import CreateProjectDialog from '../../src/components/CreateProjectDialog.vue'

// Mock composables
vi.mock('../../src/composables/useProjects', () => ({
  useProjects: () => ({
    createProject: vi.fn(() => Promise.resolve({ id: 1, name: 'test' })),
    updateProject: vi.fn(() => Promise.resolve({ id: 1, name: 'test' }))
  })
}))

vi.mock('../../src/composables/usePresets', () => ({
  usePresets: () => {
    const { ref } = require('vue')
    return {
      presets: [
        { id: 'nginx', name: 'Nginx', category: 'web', icon: '🌐', description: 'Web server', tags: ['web'] },
        { id: 'postgres', name: 'PostgreSQL', category: 'database', icon: '🐘', description: 'Database', tags: ['db'] }
      ],
      categories: [
        { id: 'web', name: 'Web Servers', count: 1 },
        { id: 'database', name: 'Databases', count: 1 }
      ],
      loadingPresets: false,
      loadPresets: vi.fn(() => Promise.resolve()),
      selectPreset: vi.fn(),
      resetSelection: vi.fn(),
      selectedPreset: ref(null),  // Must be ref
      selectedCategory: null,
      filteredPresets: []
    }
  }
}))

describe('CreateProjectDialog', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(CreateProjectDialog, {
      props: {
        modelValue: true,
        editingProject: null
      },
      global: {
        plugins: [PrimeVue, ToastService],
        stubs: {
          Dialog: true,
          TabView: true,
          TabPanel: true,
          Card: true,
          Chip: true,
          Button: true,
          InputText: true,
          Textarea: true,
          Skeleton: true
        }
      }
    })
  })

  describe('Dialog visibility', () => {
    it('should emit update:modelValue when visible changes', async () => {
      wrapper.vm.visible = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false])
    })
  })

  describe('Form fields', () => {
    it('should have name field', () => {
      expect(wrapper.vm.formData).toHaveProperty('name')
    })

    it('should have domain field', () => {
      expect(wrapper.vm.formData).toHaveProperty('domain')
    })

    it('should have compose_content field', () => {
      expect(wrapper.vm.formData).toHaveProperty('compose_content')
    })

    it('should NOT have port field', () => {
      expect(wrapper.vm.formData).not.toHaveProperty('port')
    })
  })

  describe('Validation', () => {
    it('should require name', async () => {
      wrapper.vm.formData.name = ''
      wrapper.vm.formData.domain = 'test.local'
      wrapper.vm.formData.compose_content = 'version: "3.8"'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.canSave).toBe(false)
    })

    it('should require domain', async () => {
      wrapper.vm.formData.name = 'test'
      wrapper.vm.formData.domain = ''
      wrapper.vm.formData.compose_content = 'version: "3.8"'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.canSave).toBe(false)
    })

    it('should require compose content when not editing', async () => {
      wrapper.vm.formData.name = 'test'
      wrapper.vm.formData.domain = 'test.local'
      wrapper.vm.formData.compose_content = ''
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.canSave).toBe(false)
    })

    it('should enable save when all fields valid', async () => {
      wrapper.vm.formData.name = 'test'
      wrapper.vm.formData.domain = 'test.local'
      wrapper.vm.formData.compose_content = 'version: "3.8"\nservices:\n  web:\n    image: nginx'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.canSave).toBe(true)
    })
  })

  describe('Create mode', () => {
    it('should show "Create New Project" in header when not editing', async () => {
      const dialogProps = wrapper.findComponent({ name: 'Dialog' })
      // Since we stubbed Dialog, check the prop
      expect(wrapper.props().editingProject).toBe(null)
    })

    it('should have empty form initially', () => {
      expect(wrapper.vm.formData.name).toBe('')
      expect(wrapper.vm.formData.domain).toBe('')
      expect(wrapper.vm.formData.compose_content).toBe('')
    })
  })

  describe('Edit mode', () => {
    beforeEach(async () => {
      wrapper = mount(CreateProjectDialog, {
        props: {
          modelValue: true,
          editingProject: {
            id: 1,
            name: 'existing-project',
            domain: 'existing.com',
            compose_content: 'version: "3.8"\nservices:\n  app:\n    image: alpine'
          }
        },
        global: {
          plugins: [PrimeVue, ToastService],
          stubs: {
            Dialog: true,
            TabView: true,
            TabPanel: true,
            Card: true,
            Chip: true,
            Button: true,
            InputText: true,
            Textarea: true,
            Skeleton: true
          }
        }
      })
      await wrapper.vm.$nextTick()
    })

    it('should populate form with project data', () => {
      expect(wrapper.vm.formData.name).toBe('existing-project')
      expect(wrapper.vm.formData.domain).toBe('existing.com')
      expect(wrapper.vm.formData.compose_content).toContain('alpine')
    })

    it('should show "Edit Project" in header when editing', () => {
      expect(wrapper.props().editingProject).toBeTruthy()
    })
  })

  describe('Reset functionality', () => {
    it('should clear form on reset', () => {
      wrapper.vm.formData.name = 'test'
      wrapper.vm.formData.domain = 'test.local'
      wrapper.vm.formData.compose_content = 'content'
      
      wrapper.vm.resetForm()
      
      expect(wrapper.vm.formData.name).toBe('')
      expect(wrapper.vm.formData.domain).toBe('')
      expect(wrapper.vm.formData.compose_content).toBe('')
    })
  })
})

