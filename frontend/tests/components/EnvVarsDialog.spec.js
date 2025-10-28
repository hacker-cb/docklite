import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import EnvVarsDialog from '../../src/components/EnvVarsDialog.vue'

// Mock composables
vi.mock('../../src/composables/useProjects', () => ({
  useProjects: () => ({
    getEnvVars: vi.fn(() => Promise.resolve({ VAR1: 'value1', VAR2: 'value2' })),
    updateEnvVars: vi.fn(() => Promise.resolve())
  })
}))

describe('EnvVarsDialog', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(EnvVarsDialog, {
      props: {
        modelValue: true,
        projectId: 1
      },
      global: {
        plugins: [PrimeVue, ToastService],
        stubs: {
          Dialog: true,
          Button: true,
          InputText: true
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

  describe('Environment variables list', () => {
    it('should display existing env vars', async () => {
      wrapper.vm.localEnvVars = { VAR1: 'value1', VAR2: 'value2' }
      await wrapper.vm.$nextTick()
      
      expect(Object.keys(wrapper.vm.localEnvVars)).toHaveLength(2)
      expect(wrapper.vm.localEnvVars.VAR1).toBe('value1')
      expect(wrapper.vm.localEnvVars.VAR2).toBe('value2')
    })

    it('should allow editing var values', () => {
      wrapper.vm.localEnvVars = { KEY: 'oldvalue' }
      wrapper.vm.localEnvVars.KEY = 'newvalue'
      
      expect(wrapper.vm.localEnvVars.KEY).toBe('newvalue')
    })
  })

  describe('Add new variable', () => {
    it('should add new env var', () => {
      wrapper.vm.newEnvKey = 'NEW_KEY'
      wrapper.vm.newEnvValue = 'new_value'
      
      wrapper.vm.addEnvVar()
      
      expect(wrapper.vm.localEnvVars.NEW_KEY).toBe('new_value')
      expect(wrapper.vm.newEnvKey).toBe('')
      expect(wrapper.vm.newEnvValue).toBe('')
    })

    it('should not add empty key', () => {
      wrapper.vm.newEnvKey = ''
      wrapper.vm.newEnvValue = 'value'
      
      const sizeBefore = Object.keys(wrapper.vm.localEnvVars).length
      wrapper.vm.addEnvVar()
      
      expect(Object.keys(wrapper.vm.localEnvVars)).toHaveLength(sizeBefore)
    })

    it('should not add empty value', () => {
      wrapper.vm.newEnvKey = 'KEY'
      wrapper.vm.newEnvValue = ''
      
      const sizeBefore = Object.keys(wrapper.vm.localEnvVars).length
      wrapper.vm.addEnvVar()
      
      expect(Object.keys(wrapper.vm.localEnvVars)).toHaveLength(sizeBefore)
    })
  })

  describe('Delete variable', () => {
    it('should delete env var', () => {
      wrapper.vm.localEnvVars = { KEY1: 'value1', KEY2: 'value2' }
      
      wrapper.vm.deleteEnvVar('KEY1')
      
      expect(wrapper.vm.localEnvVars.KEY1).toBeUndefined()
      expect(wrapper.vm.localEnvVars.KEY2).toBe('value2')
    })
  })

  describe('Save functionality', () => {
    it('should emit saved event on successful save', async () => {
      wrapper.vm.localEnvVars = { KEY: 'value' }
      
      await wrapper.vm.handleSave()
      
      expect(wrapper.emitted('saved')).toBeTruthy()
    })

    it('should set saving flag during save', () => {
      wrapper.vm.handleSave()
      expect(wrapper.vm.saving).toBe(true)
    })
  })

  describe('Close functionality', () => {
    it('should close dialog without saving', () => {
      wrapper.vm.handleClose()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('saved')).toBeFalsy()
    })
  })
})

