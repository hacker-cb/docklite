import { describe, it, expect, beforeEach, vi } from 'vitest'
import { showSuccess, showError, showWarning, showInfo } from '../../src/utils/toast'

// Mock constants
vi.mock('../../src/config/constants', () => ({
  TOAST_DURATION: {
    SHORT: 2000,
    NORMAL: 3000,
    LONG: 5000
  },
  TOAST_SEVERITY: {
    SUCCESS: 'success',
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info'
  }
}))

// Mock formatters
vi.mock('../../src/utils/formatters', () => ({
  formatError: (error) => {
    if (typeof error === 'string') return error
    return error.message || 'Formatted error'
  }
}))

describe('toast utilities', () => {
  let mockToast

  beforeEach(() => {
    mockToast = {
      add: vi.fn()
    }
  })

  describe('showSuccess', () => {
    it('should show success toast with message', () => {
      showSuccess(mockToast, 'Operation successful')
      
      expect(mockToast.add).toHaveBeenCalledWith({
        severity: 'success',
        summary: 'Success',
        detail: 'Operation successful',
        life: 3000
      })
    })

    it('should allow custom summary', () => {
      showSuccess(mockToast, 'Saved', 'Custom Success')
      
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          summary: 'Custom Success'
        })
      )
    })
  })

  describe('showError', () => {
    it('should show error toast with string message', () => {
      showError(mockToast, 'Something failed')
      
      expect(mockToast.add).toHaveBeenCalledWith({
        severity: 'error',
        summary: 'Error',
        detail: 'Something failed',
        life: 5000
      })
    })

    it('should format error object', () => {
      const error = new Error('Network error')
      showError(mockToast, error)
      
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          severity: 'error',
          detail: 'Network error'
        })
      )
    })

    it('should allow custom summary', () => {
      showError(mockToast, 'Failed', 'Custom Error')
      
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          summary: 'Custom Error'
        })
      )
    })
  })

  describe('showWarning', () => {
    it('should show warning toast with message', () => {
      showWarning(mockToast, 'Please be careful')
      
      expect(mockToast.add).toHaveBeenCalledWith({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please be careful',
        life: 3000
      })
    })

    it('should allow custom summary', () => {
      showWarning(mockToast, 'Caution', 'Custom Warning')
      
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          summary: 'Custom Warning'
        })
      )
    })
  })

  describe('showInfo', () => {
    it('should show info toast with message', () => {
      showInfo(mockToast, 'For your information')
      
      expect(mockToast.add).toHaveBeenCalledWith({
        severity: 'info',
        summary: 'Info',
        detail: 'For your information',
        life: 2000
      })
    })

    it('should allow custom summary', () => {
      showInfo(mockToast, 'Note', 'Custom Info')
      
      expect(mockToast.add).toHaveBeenCalledWith(
        expect.objectContaining({
          summary: 'Custom Info'
        })
      )
    })
  })

  describe('Toast severities', () => {
    it('should use different severities', () => {
      showSuccess(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ severity: 'success' })
      )

      showError(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ severity: 'error' })
      )

      showWarning(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ severity: 'warn' })
      )

      showInfo(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ severity: 'info' })
      )
    })
  })

  describe('Toast durations', () => {
    it('should use different durations', () => {
      showInfo(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ life: 2000 }) // SHORT
      )

      showSuccess(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ life: 3000 }) // NORMAL
      )

      showError(mockToast, 'msg')
      expect(mockToast.add).toHaveBeenLastCalledWith(
        expect.objectContaining({ life: 5000 }) // LONG
      )
    })
  })
})

