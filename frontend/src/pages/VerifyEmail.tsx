import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';
import type { VerifyEmailResponse } from '../types/auth';

interface StatusState {
  state: 'idle' | 'verifying' | 'success' | 'error';
  message?: string;
}

export function VerifyEmail() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<StatusState>({ state: token ? 'verifying' : 'idle' });
  const [resendEmail, setResendEmail] = useState('');
  const [resendMessage, setResendMessage] = useState('');
  const [resendError, setResendError] = useState('');
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus({ state: 'idle' });
        return;
      }

      try {
        const response: VerifyEmailResponse = await authService.verifyEmail(token);
        setStatus({ state: 'success', message: response.message });
      } catch (error: unknown) {
        const message =
          (typeof error === 'object' && error !== null && 'response' in error
            ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
            : undefined) ||
          (error instanceof Error ? error.message : undefined) ||
          'Não foi possível validar este token. Solicite um novo email de verificação.';
        setStatus({ state: 'error', message });
      }
    };

    verify();
  }, [token]);

  const handleResend = async (event: React.FormEvent) => {
    event.preventDefault();
    setResendError('');
    setResendMessage('');

    if (!resendEmail) {
      setResendError('Informe o email utilizado no cadastro.');
      return;
    }

    try {
      setIsResending(true);
      const response = await authService.resendVerification(resendEmail);
      setResendMessage(response.message || 'Email de verificação reenviado com sucesso.');
    } catch (error: unknown) {
      const message =
        (typeof error === 'object' && error !== null && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined) ||
        (error instanceof Error ? error.message : undefined) ||
        'Não foi possível reenviar o email. Tente novamente mais tarde.';
      setResendError(message);
    } finally {
      setIsResending(false);
    }
  };

  const renderStatus = () => {
    switch (status.state) {
      case 'verifying':
        return (
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            <p className="text-gray-600">Validando seu token de verificação...</p>
          </div>
        );
      case 'success':
        return (
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-semibold text-green-600">Email verificado com sucesso!</h2>
            <p className="text-gray-600">{status.message}</p>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Ir para login
            </button>
          </div>
        );
      case 'error':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-red-600 text-center">Não foi possível verificar o email</h2>
            <p className="text-gray-600 text-center">{status.message}</p>
            <div className="rounded-md bg-white border border-gray-200 p-6 shadow-sm">
              <form className="space-y-4" onSubmit={handleResend}>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Informe seu email para reenviar a verificação
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={resendEmail}
                    onChange={(event) => setResendEmail(event.target.value)}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="nome@empresa.com"
                    required
                  />
                </div>
                {resendError && <p className="text-sm text-red-600">{resendError}</p>}
                {resendMessage && <p className="text-sm text-green-600">{resendMessage}</p>}
                <div className="flex items-center justify-between">
                  <button
                    type="submit"
                    disabled={isResending}
                    className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60"
                  >
                    {isResending ? 'Reenviando...' : 'Reenviar verificação'}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate('/login')}
                    className="text-sm font-medium text-blue-600 hover:text-blue-500"
                  >
                    Voltar para login
                  </button>
                </div>
              </form>
            </div>
          </div>
        );
      case 'idle':
      default:
        return (
          <div className="space-y-4 text-center">
            <h2 className="text-2xl font-semibold text-gray-800">Verifique seu email</h2>
            <p className="text-gray-600">
              Procuramos um token de verificação, mas não encontramos. Abra o link enviado para seu email ou solicite um novo envio abaixo.
            </p>
            <div className="rounded-md bg-white border border-gray-200 p-6 shadow-sm">
              <form className="space-y-4" onSubmit={handleResend}>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email utilizado no cadastro
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={resendEmail}
                    onChange={(event) => setResendEmail(event.target.value)}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    placeholder="nome@empresa.com"
                    required
                  />
                </div>
                {resendError && <p className="text-sm text-red-600">{resendError}</p>}
                {resendMessage && <p className="text-sm text-green-600">{resendMessage}</p>}
                <button
                  type="submit"
                  disabled={isResending}
                  className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60"
                >
                  {isResending ? 'Reenviando...' : 'Reenviar verificação'}
                </button>
              </form>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto">
        <div className="bg-white shadow rounded-lg p-8">
          {renderStatus()}
        </div>
      </div>
    </div>
  );
}
