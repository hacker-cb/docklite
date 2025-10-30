import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'
import ContainersView from '../src/views/ContainersView.vue'
import { containersApi } from '../src/api'

// Mock API
vi.mock('../src/api', () => ({
  containersApi: {
    getAll: vi.fn(),
    getById: vi.fn(),
    start: vi.fn(),
    stop: vi.fn(),
    restart: vi.fn(),
    remove: vi.fn(),
    getLogs: vi.fn(),
    getStats: vi.fn()
  }
}))

describe('ContainersView', () => {
  let wrapper
  let router
  
  const mockContainers = [
    {
      id: 'abc123',
      name: 'docklite-backend',
      image: 'docklite-backend',
      status: 'running',
      state: 'running',
      created: '2025-10-29T10:00:00Z',
      started: '2025-10-29T10:00:05Z',
      ports: ['8000/tcp'],
      project: '',
      service: '',
      is_system: true,
      labels: {}
    },
    {
      id: 'def456',
      name: 'test-project_web_1',
      image: 'nginx:alpine',
      status: 'running',
      state: 'running',
      created: '2025-10-29T11:00:00Z',
      started: '2025-10-29T11:00:05Z',
      ports: ['0.0.0.0:8080->80/tcp'],
      project: 'test-project',
      service: 'web',
      is_system: false,
      labels: {}
    },
    {
      id: 'ghi789',
      name: 'stopped-container',
      image: 'redis:alpine',
      status: 'exited',
      state: 'exited',
      created: '2025-10-29T09:00:00Z',
      started: '',
      ports: [],
      project: '',
      service: '',
      is_system: false,
      labels: {}
    }
  ]
  
  beforeEach(async () => {
    // Setup router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/containers',
          name: 'Containers',
          component: ContainersView
        }
      ]
    })
    
    // Reset mocks
    vi.clearAllMocks()
    
    // Mock successful API response by default
    containersApi.getAll.mockResolvedValue({
      data: {
        containers: mockContainers,
        total: mockContainers.length
      }
    })
    
    // Mount component
    wrapper = mount(ContainersView, {
      global: {
        plugins: [router, PrimeVue, ToastService, ConfirmationService],
        directives: {
          tooltip: Tooltip
        },
        stubs: {
          Toast: true,
          ConfirmDialog: true,
          DataTable: false,  // Don't stub DataTable to render actual rows
          Column: false,
          Tag: false,
          Button: true
        }
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
  })
  
  it('renders containers view correctly', () => {
    const header = wrapper.find('.view-header h2')
    expect(header.exists()).toBe(true)
    expect(header.text()).toContain('Containers')
  })
  
  it('loads and displays containers', async () => {
    expect(containersApi.getAll).toHaveBeenCalledWith(true)
    
    // Check that containers are loaded into component
    expect(wrapper.vm.containers.length).toBe(3)
  })
  
  it('filters system containers correctly', async () => {
    const vm = wrapper.vm
    
    // Initially showing all
    expect(vm.filteredContainers.length).toBe(3)
    
    // Filter by system
    vm.filter = 'system'
    await wrapper.vm.$nextTick()
    
    expect(vm.filteredContainers.length).toBe(1)
    expect(vm.filteredContainers[0].name).toBe('docklite-backend')
  })
  
  it('filters project containers correctly', async () => {
    const vm = wrapper.vm
    
    // Filter by projects
    vm.filter = 'projects'
    await wrapper.vm.$nextTick()
    
    expect(vm.filteredContainers.length).toBe(1)
    expect(vm.filteredContainers[0].name).toBe('test-project_web_1')
    expect(vm.filteredContainers[0].project).toBe('test-project')
  })
  
  it('starts container successfully', async () => {
    containersApi.start.mockResolvedValue({ data: {} })
    
    const vm = wrapper.vm
    await vm.startContainer({ id: 'ghi789', name: 'stopped-container' })
    
    expect(containersApi.start).toHaveBeenCalledWith('ghi789')
    // Should reload containers
    expect(containersApi.getAll).toHaveBeenCalled()
  })
  
  it('stops container successfully', async () => {
    containersApi.stop.mockResolvedValue({ data: {} })
    
    const vm = wrapper.vm
    await vm.stopContainer({ id: 'abc123', name: 'docklite-backend' })
    
    expect(containersApi.stop).toHaveBeenCalledWith('abc123')
    expect(containersApi.getAll).toHaveBeenCalled()
  })
  
  it('restarts container successfully', async () => {
    containersApi.restart.mockResolvedValue({ data: {} })
    
    const vm = wrapper.vm
    await vm.restartContainer({ id: 'abc123', name: 'docklite-backend' })
    
    expect(containersApi.restart).toHaveBeenCalledWith('abc123')
    expect(containersApi.getAll).toHaveBeenCalled()
  })
  
  it('shows container logs in dialog', async () => {
    const mockLogs = '2025-10-29 Log line 1\n2025-10-29 Log line 2\n'
    containersApi.getLogs.mockResolvedValue({ data: { logs: mockLogs } })
    
    const vm = wrapper.vm
    await vm.showLogs({ id: 'abc123', name: 'docklite-backend' })
    
    expect(vm.logsDialog).toBe(true)
    expect(vm.selectedContainer.name).toBe('docklite-backend')
    expect(vm.containerLogs).toBe(mockLogs)
    expect(containersApi.getLogs).toHaveBeenCalledWith('abc123', 100)
  })
  
  it('refreshes logs with custom tail', async () => {
    const mockLogs = 'logs...'
    containersApi.getLogs.mockResolvedValue({ data: { logs: mockLogs } })
    
    const vm = wrapper.vm
    vm.selectedContainer = { id: 'abc123', name: 'test' }
    vm.logsTail = 200
    
    await vm.refreshLogs()
    
    expect(containersApi.getLogs).toHaveBeenCalledWith('abc123', 200)
  })
  
  it('toggles show all containers', async () => {
    const vm = wrapper.vm
    
    expect(vm.showAll).toBe(true)
    
    await vm.toggleShowAll()
    
    expect(vm.showAll).toBe(false)
    expect(containersApi.getAll).toHaveBeenCalledWith(false)
  })
  
  it('returns correct status icon', () => {
    const vm = wrapper.vm
    
    expect(vm.getStatusIcon('running')).toContain('text-green')
    expect(vm.getStatusIcon('exited')).toContain('text-red')
    expect(vm.getStatusIcon('paused')).toContain('text-orange')
  })
  
  it('returns correct status severity', () => {
    const vm = wrapper.vm
    
    expect(vm.getStatusSeverity('running')).toBe('success')
    expect(vm.getStatusSeverity('exited')).toBe('danger')
    expect(vm.getStatusSeverity('paused')).toBe('warning')
  })
  
  it('applies correct row class for system containers', () => {
    const vm = wrapper.vm
    
    expect(vm.getRowClass({ is_system: true })).toBe('system-row')
    expect(vm.getRowClass({ is_system: false })).toBe('')
  })
  
  it('handles API errors gracefully', async () => {
    containersApi.getAll.mockRejectedValue(new Error('API Error'))
    
    // Remount to trigger error
    wrapper = mount(ContainersView, {
      global: {
        plugins: [router, PrimeVue, ToastService, ConfirmationService],
        directives: { tooltip: Tooltip },
        stubs: { Toast: true, ConfirmDialog: true }
      }
    })
    
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Should not crash
    expect(wrapper.exists()).toBe(true)
  })
})



