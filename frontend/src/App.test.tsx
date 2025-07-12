import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'

import App from './App'

// Mock fetch globally
beforeEach(() => {
  // Reset fetch mock before each test
  globalThis.mockFetch({ status: 'healthy' })
})

describe('App Component', () => {
  it('renders the main heading', () => {
    render(<App />)
    
    const heading = screen.getByText('Sistema de Agendamento Clínico')
    expect(heading).toBeInTheDocument()
  })

  it('renders welcome message', () => {
    render(<App />)
    
    const welcomeMessage = screen.getByText('Bem-vindo ao sistema de agendamento de consultas')
    expect(welcomeMessage).toBeInTheDocument()
  })

  it('renders copyright footer', () => {
    render(<App />)
    
    const copyright = screen.getByText('© 2025 Clinic Appointment System')
    expect(copyright).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    render(<App />)
    
    const loadingText = screen.getByText('Carregando...')
    expect(loadingText).toBeInTheDocument()
  })

  it('displays API status after successful fetch', async () => {
    const mockData = {
      status: 'healthy',
      service: 'clinic-appointment-api',
      version: '1.0.0',
      environment: 'test'
    }
    
    globalThis.mockFetch(mockData)
    
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('healthy')).toBeInTheDocument()
    })
    
    expect(screen.getByText(/Versão: 1\.0\.0/)).toBeInTheDocument()
    expect(screen.getByText(/Ambiente: test/)).toBeInTheDocument()
  })

  it('displays error message when API fetch fails', async () => {
    globalThis.mockFetchError('Network error')
    
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to connect to backend API')).toBeInTheDocument()
    })
    
    expect(screen.queryByText('Carregando...')).not.toBeInTheDocument()
  })

  it('has correct CSS classes for styling', () => {
    render(<App />)
    
    const mainContainer = screen.getByText('Sistema de Agendamento Clínico').closest('div')
    expect(mainContainer).toHaveClass('bg-white', 'p-8', 'rounded-lg', 'shadow-md', 'w-96')
  })

  it('renders status section with correct heading', () => {
    render(<App />)
    
    const statusHeading = screen.getByText('Status da API')
    expect(statusHeading).toBeInTheDocument()
    expect(statusHeading).toHaveClass('text-lg', 'font-semibold', 'mb-2')
  })
})