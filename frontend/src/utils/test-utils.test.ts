import { describe, it, expect } from 'vitest'

import { formatApiStatus, isDevelopment, getApiBaseUrl, formatErrorMessage } from './test-utils'

describe('Test Utils', () => {
  describe('formatApiStatus', () => {
    it('should capitalize first letter and lowercase the rest', () => {
      expect(formatApiStatus('healthy')).toBe('Healthy')
      expect(formatApiStatus('UNHEALTHY')).toBe('Unhealthy')
      expect(formatApiStatus('operational')).toBe('Operational')
    })

    it('should handle empty string', () => {
      expect(formatApiStatus('')).toBe('')
    })

    it('should handle single character', () => {
      expect(formatApiStatus('a')).toBe('A')
    })
  })

  describe('isDevelopment', () => {
    it('should return boolean value', () => {
      const result = isDevelopment()
      expect(typeof result).toBe('boolean')
    })
  })

  describe('getApiBaseUrl', () => {
    it('should return default URL when window is undefined', () => {
      // In test environment, window might not be available or mocked
      const result = getApiBaseUrl()
      expect(typeof result).toBe('string')
      expect(result).toMatch(/^https?:\/\//)
    })
  })

  describe('formatErrorMessage', () => {
    it('should format Error objects', () => {
      const error = new Error('Test error message')
      expect(formatErrorMessage(error)).toBe('Test error message')
    })

    it('should format string errors', () => {
      expect(formatErrorMessage('String error')).toBe('String error')
    })

    it('should handle unknown error types', () => {
      expect(formatErrorMessage(null)).toBe('An unexpected error occurred')
      expect(formatErrorMessage(undefined)).toBe('An unexpected error occurred')
      expect(formatErrorMessage(123)).toBe('An unexpected error occurred')
      expect(formatErrorMessage({})).toBe('An unexpected error occurred')
    })
  })
})