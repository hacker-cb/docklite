/**
 * Formatting utilities
 */

/**
 * Format date to locale string
 * @param {string|Date} dateString - Date to format
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

/**
 * Parse FastAPI validation error to readable message
 * @param {object} error - Axios error object
 * @returns {string} Readable error message
 */
export const formatError = (error) => {
  if (!error?.response?.data?.detail) {
    return error.message || 'An error occurred'
  }

  const detail = error.response.data.detail

  // Handle FastAPI 422 validation errors
  if (error.response.status === 422 && Array.isArray(detail)) {
    const fieldErrors = detail.map(d => {
      const field = d.loc?.[d.loc.length - 1] || 'field'
      return `${field}: ${d.msg}`
    }).join(', ')
    return fieldErrors
  }

  // Handle string detail
  if (typeof detail === 'string') {
    return detail
  }

  return 'Operation failed'
}

