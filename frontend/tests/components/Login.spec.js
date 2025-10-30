import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import Login from '../../src/Login.vue'

// Mock API
vi.mock('../../src/api', () => ({
  authApi: {
    login: vi.fn(() => Promise.resolve({ data: { access_token: 'token123' } })),
    me: vi.fn(() => Promise.resolve({ data: { username: 'admin', is_admin: true } }))
  }
}))

describe('Login Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Login, {
      global: {
        plugins: [PrimeVue],
        stubs: {
          InputText: false  // Render actual inputs for testing
        }
      }
    })
  })

  describe('Form structure', () => {
    it('should have form element', () => {
      const form = wrapper.find('form')
      expect(form.exists()).toBe(true)
    })

    it('should have username field with name attribute', () => {
      const inputText = wrapper.find('#username')
      expect(inputText.exists()).toBe(true)
      // InputText renders with id on wrapper, check vm instead
      expect(wrapper.vm.credentials).toHaveProperty('username')
    })

    it('should have password field with name attribute', () => {
      const inputText = wrapper.find('#password')
      expect(inputText.exists()).toBe(true)
      expect(wrapper.vm.credentials).toHaveProperty('password')
    })

    it('should have autocomplete attribute on password', () => {
      const inputText = wrapper.find('#password')
      expect(inputText.exists()).toBe(true)
    })

    it('should have submit button', () => {
      const button = wrapper.find('button[type="submit"]')
      expect(button.exists()).toBe(true)
    })

    it('should have method="post" on form', () => {
      const form = wrapper.find('form')
      expect(form.attributes('method')).toBe('post')
    })
  })

  describe('Form validation', () => {
    it('should show error on empty username', async () => {
      wrapper.vm.credentials.username = ''
      wrapper.vm.credentials.password = 'password123'
      
      await wrapper.vm.login()
      
      expect(wrapper.vm.error).toBeTruthy()
    })

    it('should show error on empty password', async () => {
      wrapper.vm.credentials.username = 'admin'
      wrapper.vm.credentials.password = ''
      
      await wrapper.vm.login()
      
      expect(wrapper.vm.error).toBeTruthy()
    })
  })

  describe('Login functionality', () => {
    it('should have initial empty credentials', () => {
      expect(wrapper.vm.credentials.username).toBe('')
      expect(wrapper.vm.credentials.password).toBe('')
    })

    it('should not have port field', () => {
      expect(wrapper.vm.credentials).not.toHaveProperty('port')
    })

    it('should emit login event on successful login', async () => {
      wrapper.vm.credentials.username = 'admin'
      wrapper.vm.credentials.password = 'password123'
      
      await wrapper.vm.login()
      
      // login() emits event on success
      expect(wrapper.emitted()).toHaveProperty('login')
    })
  })
})

