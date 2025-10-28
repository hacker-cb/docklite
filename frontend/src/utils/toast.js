/**
 * Toast notification helpers
 */
import { TOAST_DURATION, TOAST_SEVERITY } from '../config/constants'
import { formatError } from './formatters'

/**
 * Show success toast
 * @param {object} toast - PrimeVue toast instance
 * @param {string} message - Success message
 * @param {string} summary - Toast summary (default: 'Success')
 */
export const showSuccess = (toast, message, summary = 'Success') => {
  toast.add({
    severity: TOAST_SEVERITY.SUCCESS,
    summary,
    detail: message,
    life: TOAST_DURATION.NORMAL
  })
}

/**
 * Show error toast
 * @param {object} toast - PrimeVue toast instance
 * @param {string|Error} error - Error message or object
 * @param {string} summary - Toast summary (default: 'Error')
 */
export const showError = (toast, error, summary = 'Error') => {
  const message = typeof error === 'string' ? error : formatError(error)
  
  toast.add({
    severity: TOAST_SEVERITY.ERROR,
    summary,
    detail: message,
    life: TOAST_DURATION.LONG
  })
}

/**
 * Show warning toast
 * @param {object} toast - PrimeVue toast instance
 * @param {string} message - Warning message
 * @param {string} summary - Toast summary (default: 'Warning')
 */
export const showWarning = (toast, message, summary = 'Warning') => {
  toast.add({
    severity: TOAST_SEVERITY.WARN,
    summary,
    detail: message,
    life: TOAST_DURATION.NORMAL
  })
}

/**
 * Show info toast
 * @param {object} toast - PrimeVue toast instance
 * @param {string} message - Info message
 * @param {string} summary - Toast summary (default: 'Info')
 */
export const showInfo = (toast, message, summary = 'Info') => {
  toast.add({
    severity: TOAST_SEVERITY.INFO,
    summary,
    detail: message,
    life: TOAST_DURATION.SHORT
  })
}

