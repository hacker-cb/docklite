import { describe, it, expect } from 'vitest'
import { formatDate, formatError } from '../../src/utils/formatters'

describe('formatters utilities', () => {
  describe('formatDate', () => {
    it('should format date string to locale string', () => {
      const date = '2024-01-15T12:30:00'
      const result = formatDate(date)
      
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
      // Contains date parts
      expect(result).toMatch(/2024/)
    })

    it('should handle Date objects', () => {
      const date = new Date('2024-01-15T12:30:00')
      const result = formatDate(date)
      
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('should return empty string for null', () => {
      expect(formatDate(null)).toBe('')
    })

    it('should return empty string for undefined', () => {
      expect(formatDate(undefined)).toBe('')
    })

    it('should return empty string for empty string', () => {
      expect(formatDate('')).toBe('')
    })
  })

  describe('formatError', () => {
    it('should format simple error message', () => {
      const error = new Error('Something went wrong')
      const result = formatError(error)
      
      expect(result).toBe('Something went wrong')
    })

    it('should format string detail from API response', () => {
      const error = {
        response: {
          status: 400,
          data: {
            detail: 'Invalid input'
          }
        }
      }
      const result = formatError(error)
      
      expect(result).toBe('Invalid input')
    })

    it('should format FastAPI 422 validation errors', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: [
              { loc: ['body', 'name'], msg: 'field required' },
              { loc: ['body', 'email'], msg: 'invalid email format' }
            ]
          }
        }
      }
      const result = formatError(error)
      
      expect(result).toContain('name: field required')
      expect(result).toContain('email: invalid email format')
    })

    it('should handle validation error without loc', () => {
      const error = {
        response: {
          status: 422,
          data: {
            detail: [
              { msg: 'validation failed' }
            ]
          }
        }
      }
      const result = formatError(error)
      
      expect(result).toContain('field: validation failed')
    })

    it('should return default message for unknown error', () => {
      const error = {}
      const result = formatError(error)
      
      expect(result).toBe('An error occurred')
    })

    it('should return default message when detail is not string or array', () => {
      const error = {
        response: {
          status: 400,
          data: {
            detail: { complex: 'object' }
          }
        }
      }
      const result = formatError(error)
      
      expect(result).toBe('Operation failed')
    })
  })
})

