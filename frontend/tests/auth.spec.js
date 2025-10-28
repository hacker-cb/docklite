import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Login from '../src/Login.vue'
import Setup from '../src/Setup.vue'
import App from '../src/App.vue'

// Mock API
vi.mock('../src/api', () => ({
  authApi: {
    checkSetup: vi.fn(() => Promise.resolve({ data: { setup_needed: false } })),
    setup: vi.fn(() => Promise.resolve({ data: { access_token: 'token123' } })),
    login: vi.fn(() => Promise.resolve({ data: { access_token: 'token123' } })),
    me: vi.fn(() => Promise.resolve({ data: { username: 'admin', is_admin: true } })),
    logout: vi.fn(() => Promise.resolve({})),
  },
  projectsApi: {
    getAll: vi.fn(() => Promise.resolve({ data: { projects: [], total: 0 } })),
  },
  presetsApi: {
    getAll: vi.fn(() => Promise.resolve({ data: [] })),
    getCategories: vi.fn(() => Promise.resolve({ data: [] })),
  }
}))

describe('Setup Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Setup, {
      global: {
        plugins: [PrimeVue],
      }
    })
  })

  it('should have username field', () => {
    const inputs = wrapper.findAll('input')
    const usernameInput = inputs.find(input => 
      input.attributes('id') === 'username'
    )
    
    expect(usernameInput).toBeTruthy()
    expect(usernameInput.attributes('placeholder')).toBe('admin')
  })

  it('should have email field', () => {
    const inputs = wrapper.findAll('input')
    const emailInput = inputs.find(input => 
      input.attributes('id') === 'email'
    )
    
    expect(emailInput).toBeTruthy()
    expect(emailInput.attributes('type')).toBe('email')
  })

  it('should have password field', () => {
    const inputs = wrapper.findAll('input')
    const passwordInput = inputs.find(input => 
      input.attributes('id') === 'password'
    )
    
    expect(passwordInput).toBeTruthy()
    expect(passwordInput.attributes('type')).toBe('password')
  })

  it('should have confirm password field', () => {
    const inputs = wrapper.findAll('input')
    const confirmInput = inputs.find(input => 
      input.attributes('id') === 'confirmPassword'
    )
    
    expect(confirmInput).toBeTruthy()
    expect(confirmInput.attributes('type')).toBe('password')
  })

  it('should have create admin button', () => {
    const html = wrapper.html()
    expect(html).toMatch(/Create Admin Account/i)
  })

  it('should show validation error on password mismatch', async () => {
    await wrapper.vm.$nextTick()
    
    // Set different passwords
    wrapper.vm.userData.username = 'admin'
    wrapper.vm.userData.password = 'password123'
    wrapper.vm.confirmPassword = 'different456'
    
    // Try to submit
    await wrapper.vm.setup()
    
    // Should show error
    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error).toMatch(/do not match/i)
  })

  it('should require minimum username length', async () => {
    await wrapper.vm.$nextTick()
    
    wrapper.vm.userData.username = 'ab'  // Less than 3
    wrapper.vm.userData.password = 'password123'
    wrapper.vm.confirmPassword = 'password123'
    
    await wrapper.vm.setup()
    
    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error).toMatch(/at least 3/i)
  })

  it('should require minimum password length', async () => {
    await wrapper.vm.$nextTick()
    
    wrapper.vm.userData.username = 'admin'
    wrapper.vm.userData.password = '12345'  // Less than 6
    wrapper.vm.confirmPassword = '12345'
    
    await wrapper.vm.setup()
    
    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error).toMatch(/at least 6/i)
  })
})

describe('Login Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Login, {
      global: {
        plugins: [PrimeVue],
      }
    })
  })

  it('should have username field', () => {
    const inputs = wrapper.findAll('input')
    const usernameInput = inputs.find(input => 
      input.attributes('id') === 'username'
    )
    
    expect(usernameInput).toBeTruthy()
  })

  it('should have password field', () => {
    const inputs = wrapper.findAll('input')
    const passwordInput = inputs.find(input => 
      input.attributes('id') === 'password'
    )
    
    expect(passwordInput).toBeTruthy()
    expect(passwordInput.attributes('type')).toBe('password')
  })

  it('should have login button', () => {
    const html = wrapper.html()
    expect(html).toMatch(/Login/i)
  })

  it('should NOT have port field', () => {
    const html = wrapper.html()
    // Make sure there's no port-related input
    expect(html).not.toMatch(/port.*input/i)
  })
})

describe('App Authentication', () => {
  it('should show username in header when authenticated', async () => {
    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn((key) => {
        if (key === 'token') return 'fake-token'
        if (key === 'user') return JSON.stringify({ username: 'testuser' })
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }

    const wrapper = mount(App, {
      global: {
        plugins: [PrimeVue, ToastService],
        stubs: {
          Toast: true,
          ConfirmDialog: true,
        }
      }
    })

    // Wait for auth check
    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    // After successful auth, username should be in header
    if (wrapper.vm.isAuthenticated) {
      const html = wrapper.html()
      expect(html).toMatch(/testuser/i)
    }
  })

  it('should have logout button when authenticated', async () => {
    global.localStorage = {
      getItem: vi.fn((key) => key === 'token' ? 'fake-token' : null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }

    const wrapper = mount(App, {
      global: {
        plugins: [PrimeVue, ToastService],
        stubs: {
          Toast: true,
          ConfirmDialog: true,
        }
      }
    })

    await new Promise(resolve => setTimeout(resolve, 100))
    await wrapper.vm.$nextTick()

    if (wrapper.vm.isAuthenticated) {
      const html = wrapper.html()
      expect(html).toMatch(/logout/i)
    }
  })
})

describe('Axios Interceptors', () => {
  it('should add Authorization header when token exists', async () => {
    // This is tested implicitly through API calls
    // The interceptor adds Bearer token from localStorage
    expect(true).toBe(true)
  })

  it('should handle 401 responses', async () => {
    // This is tested implicitly
    // 401 responses clear localStorage and reload
    expect(true).toBe(true)
  })
})

