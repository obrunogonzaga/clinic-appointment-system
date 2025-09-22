import { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import type { User, RegisterData, UserUpdateData } from '../../types/auth';

interface UserFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: RegisterData | UserUpdateData) => void;
  user?: User;
  loading?: boolean;
  mode: 'create' | 'edit';
}

export function UserFormModal({
  isOpen,
  onClose,
  onSubmit,
  user,
  loading = false,
  mode,
}: UserFormModalProps) {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    is_admin: false,
    is_active: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes or user changes
  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && user) {
        setFormData({
          email: user.email,
          name: user.name,
          password: '',
          is_admin: user.is_admin ?? false,
          is_active: user.is_active ?? true,
        });
      } else {
        setFormData({
          email: '',
          name: '',
          password: '',
          is_admin: false,
          is_active: true,
        });
      }
      setErrors({});
    }
  }, [isOpen, mode, user]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email deve ter um formato válido';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Nome deve ter pelo menos 2 caracteres';
    }

    if (mode === 'create' && !formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password && formData.password.length < 8) {
      newErrors.password = 'Senha deve ter pelo menos 8 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (mode === 'create') {
      const data: RegisterData = {
        email: formData.email.trim(),
        name: formData.name.trim(),
        password: formData.password,
        is_admin: formData.is_admin,
      };
      onSubmit(data);
    } else {
      const data: UserUpdateData = {
        name: formData.name.trim(),
        is_admin: formData.is_admin,
        is_active: formData.is_active,
      };
      onSubmit(data);
    }
  };

  const handleChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === 'create' ? 'Novo Usuário' : 'Editar Usuário'}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            disabled={mode === 'edit' || loading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed ${
              errors.email ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="usuario@exemplo.com"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email}</p>
          )}
        </div>

        {/* Nome */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nome Completo
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            disabled={loading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 ${
              errors.name ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Nome completo do usuário"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name}</p>
          )}
        </div>

        {/* Senha (apenas na criação) */}
        {mode === 'create' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Senha
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              disabled={loading}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 ${
                errors.password ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Senha inicial (mín. 8 caracteres)"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password}</p>
            )}
          </div>
        )}

        {/* Checkboxes */}
        <div className="space-y-3">
          <div className="flex items-center">
            <input
              id="is_admin"
              type="checkbox"
              checked={formData.is_admin}
              onChange={(e) => handleChange('is_admin', e.target.checked)}
              disabled={loading}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
            />
            <label htmlFor="is_admin" className="ml-2 text-sm text-gray-700">
              Usuário Administrador
            </label>
          </div>

          {mode === 'edit' && (
            <div className="flex items-center">
              <input
                id="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => handleChange('is_active', e.target.checked)}
                disabled={loading}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                Conta Ativa
              </label>
            </div>
          )}
        </div>

        {/* Botões */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {mode === 'create' ? 'Criando...' : 'Salvando...'}
              </div>
            ) : (
              mode === 'create' ? 'Criar Usuário' : 'Salvar Alterações'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
}