/**
 * Login page component
 */

import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { LoginCredentials } from '../types/auth';

export function Login() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAccountLocked, setIsAccountLocked] = useState(false);
  const [awaitingApproval, setAwaitingApproval] = useState(false);
  const [needsEmailVerification, setNeedsEmailVerification] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated && !isLoading) {
    return <Navigate to="/" replace />;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
    if (isAccountLocked) {
      setIsAccountLocked(false);
    }
    if (awaitingApproval) {
      setAwaitingApproval(false);
    }
    if (needsEmailVerification) {
      setNeedsEmailVerification(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!credentials.email || !credentials.password) {
      setError('Por favor, preencha todos os campos');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      setIsAccountLocked(false);
      setAwaitingApproval(false);
      setNeedsEmailVerification(false);
      
      await login(credentials);
      
      // Redirect to home page on successful login
      navigate('/', { replace: true });
      
    } catch (err: unknown) {
      const apiMessage =
        typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      const fallbackMessage = err instanceof Error ? err.message : undefined;
      const message = apiMessage || fallbackMessage || 'Erro ao fazer login';
      setError(message);

      const normalized = message.toLowerCase();
      setIsAccountLocked(normalized.includes('conta bloqueada'));
      setAwaitingApproval(normalized.includes('aguardando aprovação'));
      setNeedsEmailVerification(normalized.includes('verifique seu email'));
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
            Faça login na sua conta
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sistema de Agendamento de Clínica
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={credentials.email}
                onChange={handleInputChange}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Endereço de email"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={credentials.password}
                onChange={handleInputChange}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Senha"
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">
                {error}
              </div>
            </div>
          )}

          {isAccountLocked && (
            <div className="rounded-md border border-yellow-200 bg-yellow-50 p-4">
              <p className="text-sm text-yellow-800">
                Sua conta está temporariamente bloqueada após várias tentativas de acesso. Aguarde alguns minutos e tente novamente ou contate o suporte se precisar de liberação imediata.
              </p>
            </div>
          )}

          {awaitingApproval && (
            <div className="rounded-md border border-blue-200 bg-blue-50 p-4">
              <p className="text-sm text-blue-800">
                Seu cadastro está aguardando aprovação do administrador. Você receberá um email assim que o acesso for liberado.
              </p>
            </div>
          )}

          {needsEmailVerification && (
            <div className="rounded-md border border-indigo-200 bg-indigo-50 p-4">
              <p className="text-sm text-indigo-800">
                Antes de entrar, confirme seu endereço de email. Se não encontrou a mensagem na inbox, cheque a caixa de spam ou solicite um novo envio.
              </p>
              <button
                type="button"
                onClick={() => navigate('/verify-email')}
                className="mt-3 inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
              >
                Abrir página de verificação
              </button>
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
                  Entrando...
                </div>
              ) : (
                'Entrar'
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Primeiro acesso?{' '}
              <button
                type="button"
                onClick={() => navigate('/setup')}
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Configure o administrador
              </button>
            </p>
            <p className="mt-2 text-sm text-gray-600">
              É colaborador da clínica?{' '}
              <button
                type="button"
                onClick={() => navigate('/register')}
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Solicite acesso
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
