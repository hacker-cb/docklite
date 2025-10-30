import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import DeployInfoDialog from '../../src/components/DeployInfoDialog.vue'

// Mock API
vi.mock('../../src/api', () => ({
  deploymentApi: {
    getInfo: vi.fn(() => Promise.resolve({
      data: {
        project_id: 1,
        project_name: 'test-project',
        domain: 'test.local',
        project_path: '/home/docklite/projects/1',
        deploy_user: 'docklite',
        server: 'localhost',
        instructions: {
          upload_files: 'rsync -avz ./ docklite@localhost:/home/docklite/projects/1/',
          start_containers: 'ssh docklite@localhost "cd /home/docklite/projects/1 && docker-compose up -d"',
          check_status: 'ssh docklite@localhost "cd /home/docklite/projects/1 && docker-compose ps"',
          view_logs: 'ssh docklite@localhost "cd /home/docklite/projects/1 && docker-compose logs -f"',
          restart: 'ssh docklite@localhost "cd /home/docklite/projects/1 && docker-compose restart"',
          stop: 'ssh docklite@localhost "cd /home/docklite/projects/1 && docker-compose down"'
        },
        examples: {
          deploy_script: '#!/bin/bash\nrsync -avz ./ docklite@localhost:/path',
          ssh_config: 'Host docklite-1\n  HostName localhost\n  User docklite'
        }
      }
    }))
  }
}))

describe('DeployInfoDialog', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = mount(DeployInfoDialog, {
      props: {
        modelValue: false,  // Start closed
        projectId: 1
      },
      global: {
        plugins: [PrimeVue, ToastService],
        stubs: {
          Dialog: true,
          Button: true
        }
      }
    })
    // Open dialog to trigger watch
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()
    await flushPromises()
  })

  describe('Dialog visibility', () => {
    it('should emit update:modelValue when visible changes', async () => {
      wrapper.vm.visible = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false])
    })
  })

  describe('Deployment info loading', () => {
    it('should load deployment info on mount', async () => {
      expect(wrapper.vm.deployInfo).toBeTruthy()
      expect(wrapper.vm.deployInfo.project_id).toBe(1)
    })

    it('should display project information', async () => {
      expect(wrapper.vm.deployInfo).toBeTruthy()
      expect(wrapper.vm.deployInfo.domain).toBe('test.local')
      expect(wrapper.vm.deployInfo.project_path).toContain('/home/docklite/projects/1')
    })

    it('should display deployment instructions', async () => {
      expect(wrapper.vm.deployInfo).toBeTruthy()
      expect(wrapper.vm.deployInfo.instructions.upload_files).toContain('rsync')
      expect(wrapper.vm.deployInfo.instructions.start_containers).toContain('docker-compose up -d')
    })

    it('should display deploy script example', async () => {
      expect(wrapper.vm.deployInfo.examples.deploy_script).toContain('#!/bin/bash')
    })

    it('should display ssh config example', async () => {
      expect(wrapper.vm.deployInfo.examples.ssh_config).toContain('Host docklite-')
    })
  })

  describe('Close functionality', () => {
    it('should close dialog', () => {
      wrapper.vm.handleClose()
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })
  })
})

