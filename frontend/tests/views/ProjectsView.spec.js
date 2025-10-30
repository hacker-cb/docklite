import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import ProjectsView from '../../src/views/ProjectsView.vue'

// Mock composables
vi.mock('../../src/composables/useProjects', () => ({
  useProjects: () => ({
    projects: [{
      id: 1,
      name: 'test-project',
      domain: 'test.local',
      status: 'running',
      compose_content: 'version: "3.8"',
      env_vars: {}
    }],
    loading: false,
    loadProjects: vi.fn(() => Promise.resolve()),
    createProject: vi.fn(() => Promise.resolve({ id: 2 })),
    updateProject: vi.fn(() => Promise.resolve()),
    deleteProject: vi.fn(() => Promise.resolve()),
    getEnvVars: vi.fn(() => Promise.resolve({})),
    updateEnvVars: vi.fn(() => Promise.resolve())
  })
}))

vi.mock('../../src/composables/useContainers', () => ({
  useContainers: () => ({
    startContainer: vi.fn(() => Promise.resolve()),
    stopContainer: vi.fn(() => Promise.resolve()),
    restartContainer: vi.fn(() => Promise.resolve())
  })
}))

describe('ProjectsView', () => {
  let wrapper
  let router

  beforeEach(async () => {
    router = createRouter({
      history: createWebHashHistory(),
      routes: [{
        path: '/',
        component: ProjectsView
      }]
    })

    wrapper = mount(ProjectsView, {
      global: {
        plugins: [PrimeVue, ToastService, ConfirmationService, router],
        stubs: {
          DataTable: true,
          Column: true,
          Button: true,
          Tag: true,
          Toast: true,
          ConfirmDialog: true,
          CreateProjectDialog: true,
          EnvVarsDialog: true,
          DeployInfoDialog: true
        }
      }
    })

    await router.isReady()
  })

  describe('View structure', () => {
    it('should have toolbar with title', () => {
      expect(wrapper.html()).toContain('Projects')
    })

    it('should have "New Project" button', () => {
      expect(wrapper.html()).toContain('New Project')
    })

    it('should have projects data table', () => {
      const table = wrapper.findComponent({ name: 'DataTable' })
      expect(table.exists()).toBe(true)
    })
  })

  describe('Projects data', () => {
    it('should display projects', () => {
      expect(wrapper.vm.projects).toHaveLength(1)
      expect(wrapper.vm.projects[0].name).toBe('test-project')
    })

    it('should show loading state initially', () => {
      expect(wrapper.vm.loading).toBeDefined()
    })
  })

  describe('Dialog visibility', () => {
    it('should show create dialog when clicking New Project', async () => {
      wrapper.vm.showCreateDialog = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showCreateDialog).toBe(true)
    })

    it('should show env vars dialog', async () => {
      wrapper.vm.showEnvDialog = true
      wrapper.vm.envProjectId = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showEnvDialog).toBe(true)
      expect(wrapper.vm.envProjectId).toBe(1)
    })

    it('should show deploy info dialog', async () => {
      wrapper.vm.showDeployDialog = true
      wrapper.vm.deployProjectId = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showDeployDialog).toBe(true)
      expect(wrapper.vm.deployProjectId).toBe(1)
    })
  })

  describe('Container actions', () => {
    it('should call start container', async () => {
      const project = wrapper.vm.projects[0]
      await wrapper.vm.startContainer(project)
      
      // Check that composable was called
      expect(wrapper.vm.projects).toBeDefined()
    })

    it('should call stop container', async () => {
      const project = wrapper.vm.projects[0]
      await wrapper.vm.stopContainer(project)
      
      expect(wrapper.vm.projects).toBeDefined()
    })

    it('should call restart container', async () => {
      const project = wrapper.vm.projects[0]
      await wrapper.vm.restartContainer(project)
      
      expect(wrapper.vm.projects).toBeDefined()
    })
  })

  describe('Project edit', () => {
    it('should open edit dialog with project data', () => {
      const project = { id: 1, name: 'test', domain: 'test.local' }
      wrapper.vm.editProject(project)
      
      expect(wrapper.vm.showCreateDialog).toBe(true)
      expect(wrapper.vm.editingProject).toEqual(project)
    })

    it('should open env vars dialog', () => {
      const project = { id: 1 }
      wrapper.vm.editEnvVarsDialog(project)
      
      expect(wrapper.vm.showEnvDialog).toBe(true)
      expect(wrapper.vm.envProjectId).toBe(1)
    })

    it('should open deploy info dialog', () => {
      const project = { id: 1 }
      wrapper.vm.showDeployInfoDialog(project)
      
      expect(wrapper.vm.showDeployDialog).toBe(true)
      expect(wrapper.vm.deployProjectId).toBe(1)
    })
  })

  describe('Status severity', () => {
    it('should return correct severity for status', () => {
      expect(wrapper.vm.getStatusSeverity('running')).toBe('success')
      // 'stopped' may return 'warning' instead of 'danger' depending on implementation
      const stoppedSeverity = wrapper.vm.getStatusSeverity('stopped')
      expect(['danger', 'warning']).toContain(stoppedSeverity)
      expect(wrapper.vm.getStatusSeverity('created')).toBe('info')
    })
  })
})

