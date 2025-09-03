/**
 * Setup page for admin registration
 */

import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { RegisterData } from '../types/auth';

export function Setup() {
  const { register, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  
  const [setupData, setSetupData] = useState<RegisterData>({
    email: '',
    name: '',
    password: '',
    is_admin: true,
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated && !isLoading) {
    return <Navigate to="/" replace />;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setSetupData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
    
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const validateForm = (): boolean => {
    if (!setupData.email || !setupData.name || !setupData.password) {
      setError('Por favor, preencha todos os campos');
      return false;
    }

    if (setupData.password.length < 8) {
      setError('A senha deve ter pelo menos 8 caracteres');
      return false;
    }

    if (setupData.password !== confirmPassword) {
      setError('As senhas não conferem');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      
      await register(setupData);
      
      // Redirect to home page on successful registration
      navigate('/', { replace: true });
      
    } catch (err: any) {
      // Handle different types of errors
      let errorMessage = 'Erro ao criar administrador';
      
      console.log('Error caught:', err);
      console.log('Error response:', err.response);
      console.log('Error response data:', err.response?.data);
      console.log('Error response status:', err.response?.status);
      
      if (err.response?.status === 403) {
        // Authorization error - show detailed info
        const errorData = err.response.data;
        console.log('403 Error data:', errorData);
        
        if (typeof errorData === 'object' && errorData.message) {
          errorMessage = errorData.message;
          console.log('Using errorData.message:', errorMessage);
        } else if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
          console.log('Using response.data.detail:', errorMessage);
        } else {
          errorMessage = errorData.detail || errorMessage;
          console.log('Using errorData.detail or default:', errorMessage);
        }
      } else {
        // Other errors
        errorMessage = err.response?.data?.detail || err.message || errorMessage;
        console.log('Non-403 error message:', errorMessage);
      }
      
      console.log('Final error message:', errorMessage);
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Cadastro de Administrador
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Crie uma nova conta de administrador do sistema
          </p>
          <div className="mt-4 rounded-md bg-blue-50 p-4">
            <div className="text-sm text-blue-800">
              <strong>Importante:</strong> Apenas emails autorizados podem criar contas administrativas. 
              Se você encontrar erro de autorização, verifique com o responsável pelo sistema.
            </div>
          </div>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Nome completo
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={setupData.name}
                onChange={handleInputChange}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Seu nome completo"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={setupData.email}
                onChange={handleInputChange}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="seu@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={setupData.password}
                onChange={handleInputChange}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Mínimo 8 caracteres"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirmar senha
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={handleInputChange}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Digite a senha novamente"
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">
                {error}
                {(error.includes('não autorizado') || error.includes('não está autorizado')) && (
                  <div className="mt-3 p-3 bg-red-100 rounded-md">
                    <div className="text-xs">
                      <strong>🚨 Acesso Restrito</strong>
                      <p className="mt-1">
                        Apenas emails pré-autorizados podem criar contas administrativas neste sistema.
                      </p>
                      <p className="mt-2">
                        <strong>O que fazer:</strong>
                      </p>
                      <ul className="mt-1 ml-4 list-disc">
                        <li>Entre em contato com o administrador do sistema</li>
                        <li>Solicite a inclusão do seu email na lista de administradores</li>
                        <li>Aguarde a autorização antes de tentar novamente</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Criando administrador...
                </div>
              ) : (
                'Criar Administrador'
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Já possui uma conta?{' '}
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Faça login
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}