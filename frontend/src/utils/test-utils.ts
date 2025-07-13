/**
 * Test utilities for the frontend application
 */

/**
 * Simple utility function to format API status for display
 */
export const formatApiStatus = (status: string): string => {
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()
}

/**
 * Check if an environment is development
 */
export const isDevelopment = (): boolean => {
  return import.meta.env.DEV || false
}

/**
 * Get API base URL based on environment
 */
export const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return 'http://localhost:8000'
}

/**
 * Format error message for user display
 */
export const formatErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unexpected error occurred'
}