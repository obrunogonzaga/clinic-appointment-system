import { useState, useEffect } from 'react'
import './App.css'

interface HealthStatus {
  status: string
  service: string
  version: string
  environment: string
}

function App() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => {
        setHealthStatus(data)
        setLoading(false)
      })
      .catch(err => {
        setError('Failed to connect to backend API')
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-3xl font-bold text-center mb-6 text-blue-600">
          Sistema de Agendamento Clínico
        </h1>
        
        <div className="text-center">
          <p className="text-gray-600 mb-4">
            Bem-vindo ao sistema de agendamento de consultas
          </p>
          
          <div className="border-t pt-4">
            <h2 className="text-lg font-semibold mb-2">Status da API</h2>
            {loading && <p className="text-gray-500">Carregando...</p>}
            {error && <p className="text-red-500">{error}</p>}
            {healthStatus && (
              <div className="text-sm text-gray-600">
                <p>Status: <span className="text-green-500 font-semibold">{healthStatus.status}</span></p>
                <p>Versão: {healthStatus.version}</p>
                <p>Ambiente: {healthStatus.environment}</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>© 2025 Clinic Appointment System</p>
        </div>
      </div>
    </div>
  )
}

export default App