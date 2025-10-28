import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import Setup from '../../src/Setup.vue'

// Mock API
vi.mock('../../src/api', () => ({
  authApi: {
    setup: vi.fn(() => Promise.resolve({ data: { access_token: 'token123' } })),
    me: vi.fn(() => Promise.resolve({ data: { username: 'admin', is_admin: true } }))
  }
}))

describe('Setup Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Setup, {
      global: {
        plugins: [PrimeVue]
      }
    })
  })

  describe('Form structure', () => {
    it('should have form element', () => {
      const form = wrapper.find('form')
      expect(form.exists()).toBe(true)
    })

    it('should have username field with autocomplete', () => {
      const input = wrapper.find('input[id="username"]')
      expect(input.exists()).toBe(true)
      expect(input.attributes('name')).toBe('username')
      expect(input.attributes('autocomplete')).toBe('username')
      expect(input.attributes('placeholder')).toBe('admin')
    })

    it('should have email field', () => {
      const input = wrapper.find('input[id="email"]')
      expect(input.exists()).toBe(true)
      expect(input.attributes('type')).toBe('email')
      expect(input.attributes('name')).toBe('email')
    })

    it('should have password field with new-password autocomplete', () => {
      const input = wrapper.find('input[id="password"]')
      expect(input.exists()).toBe(true)
      expect(input.attributes('type')).toBe('password')
      expect(input.attributes('name')).toBe('password')
      expect(input.attributes('autocomplete')).toBe('new-password')
    })

    it('should have passwordrules for Safari', () => {
      const input = wrapper.find('input[id="password"]')
      expect(input.attributes('passwordrules')).toContain('minlength')
    })

    it('should have confirm password field', () => {
      const input = wrapper.find('input[id="confirmPassword"]')
      expect(input.exists()).toBe(true)
      expect(input.attributes('type')).toBe('password')
    })

    it('should have create admin button', () => {
      const button = wrapper.find('button[type="submit"]')
      expect(button.exists()).toBe(true)
    })

    it('should have method="post" on form', () => {
      const form = wrapper.find('form')
      expect(form.attributes('method')).toBe('post')
    })
  })

  describe('Form validation', () => {
    it('should show error on password mismatch', async () => {
      wrapper.vm.userData.username = 'admin'
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = 'password123'
      wrapper.vm.confirmPassword = 'different456'
      
      await wrapper.vm.setup()
      
      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.vm.error).toMatch(/do not match/i)
    })

    it('should require minimum username length', async () => {
      wrapper.vm.userData.username = 'ab'  // Less than 3
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      
      await wrapper.vm.setup()
      
      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.vm.error).toMatch(/at least 3/i)
    })

    it('should require minimum password length', async () => {
      wrapper.vm.userData.username = 'admin'
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = '12345'  // Less than 6
      wrapper.vm.confirmPassword = '12345'
      
      await wrapper.vm.setup()
      
      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.vm.error).toMatch(/at least 6/i)
    })

    it('should require username', async () => {
      wrapper.vm.userData.username = ''
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      
      await wrapper.vm.setup()
      
      expect(wrapper.vm.error).toBeTruthy()
    })

    it('should require password', async () => {
      wrapper.vm.userData.username = 'admin'
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = ''
      wrapper.vm.confirmPassword = ''
      
      await wrapper.vm.setup()
      
      expect(wrapper.vm.error).toBeTruthy()
    })
  })

  describe('Setup functionality', () => {
    it('should have initial empty form', () => {
      expect(wrapper.vm.userData.username).toBe('')
      expect(wrapper.vm.userData.email).toBe('')
      expect(wrapper.vm.userData.password).toBe('')
      expect(wrapper.vm.confirmPassword).toBe('')
    })

    it('should emit complete event on successful setup', async () => {
      wrapper.vm.userData.username = 'admin'
      wrapper.vm.userData.email = 'admin@example.com'
      wrapper.vm.userData.password = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      
      await wrapper.vm.setup()
      
      expect(wrapper.emitted('complete')).toBeTruthy()
    })
  })
})

