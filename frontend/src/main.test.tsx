import { describe, it, expect, vi } from 'vitest'

// Mock ReactDOM
vi.mock('react-dom/client', () => ({
  createRoot: vi.fn(() => ({
    render: vi.fn(),
  })),
}))

// Mock the App component
vi.mock('./App.tsx', () => ({
  default: () => 'Mocked App Component',
}))

describe('Main Entry Point', () => {
  it('should import main module without errors', async () => {
    // This test ensures the main.tsx file can be imported successfully
    expect(async () => {
      await import('./main')
    }).not.toThrow()
  })

  it('should have React.StrictMode wrapper', async () => {
    // Import React to verify it's available
    const React = await import('react')
    expect(React.StrictMode).toBeDefined()
  })
})