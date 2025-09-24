import { XMarkIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useState } from 'react';
import type { COLLECTOR_STATUS, Collector, CollectorFormData } from '../types/collector';

interface CollectorFormProps {
  collector?: Collector;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CollectorFormData) => void;
  isLoading?: boolean;
  serverError?: string;
  onServerErrorClear?: () => void;
}

const initialFormData: CollectorFormData = {
  nome_completo: '',
  cpf: '',
  telefone: '',
  email: '',
  data_nascimento: '',
  endereco: '',
  status: 'Ativo',
  carro: '',
  observacoes: '',
  registro_profissional: '',
  especializacao: '',
};

export const CollectorForm: React.FC<CollectorFormProps> = ({
  collector,
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  serverError,
  onServerErrorClear,
}) => {
  const [formData, setFormData] = useState<CollectorFormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<CollectorFormData>>({});

  // Reset form when modal opens/closes or collector changes
  useEffect(() => {
    if (isOpen && collector) {
      setFormData({
        nome_completo: collector.nome_completo || '',
        cpf: collector.cpf || '',
        telefone: collector.telefone || '',
        email: collector.email || '',
        data_nascimento: collector.data_nascimento ? 
          new Date(collector.data_nascimento).toISOString().split('T')[0] : '',
        endereco: collector.endereco || '',
        status: collector.status as typeof COLLECTOR_STATUS[keyof typeof COLLECTOR_STATUS] || 'Ativo',
        carro: collector.carro || '',
        observacoes: collector.observacoes || '',
        registro_profissional: collector.registro_profissional || '',
        especializacao: collector.especializacao || '',
      });
    } else if (isOpen && !collector) {
      setFormData(initialFormData);
    }
    setErrors({});
  }, [isOpen, collector]);

  const validateCPF = (cpf: string): boolean => {
    // Remove any non-digit characters
    const cleanCPF = cpf.replace(/\D/g, '');
    
    if (cleanCPF.length !== 11) {
      return false;
    }

    // Check for invalid CPFs (all same digits)
    if (cleanCPF === cleanCPF[0].repeat(11)) {
      return false;
    }

    // Convert to array of numbers
    const digits = cleanCPF.split('').map(Number);

    // First verification digit
    let sum1 = 0;
    for (let i = 0; i < 9; i++) {
      sum1 += digits[i] * (10 - i);
    }
    const remainder1 = sum1 % 11;
    const firstDigit = remainder1 < 2 ? 0 : 11 - remainder1;

    if (digits[9] !== firstDigit) {
      return false;
    }

    // Second verification digit
    let sum2 = 0;
    for (let i = 0; i < 10; i++) {
      sum2 += digits[i] * (11 - i);
    }
    const remainder2 = sum2 % 11;
    const secondDigit = remainder2 < 2 ? 0 : 11 - remainder2;

    return digits[10] === secondDigit;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    if (serverError) {
      onServerErrorClear?.();
    }

    // For CPF, only allow numbers
    if (name === 'cpf') {
      const cleanValue = value.replace(/\D/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: cleanValue
      }));
      
      // Real-time CPF validation
      if (cleanValue.length === 11) {
        if (!validateCPF(cleanValue)) {
          setErrors(prev => ({
            ...prev,
            cpf: 'CPF inválido. Verifique os dígitos.'
          }));
        } else {
          setErrors(prev => ({
            ...prev,
            cpf: undefined
          }));
        }
      } else if (cleanValue.length > 0) {
        setErrors(prev => ({
          ...prev,
          cpf: undefined
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear error when user starts typing (except for CPF which has its own validation)
    if (name !== 'cpf' && errors[name as keyof CollectorFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<CollectorFormData> = {};

    if (!formData.nome_completo.trim()) {
      newErrors.nome_completo = 'Nome completo é obrigatório';
    }

    if (!formData.cpf.trim()) {
      newErrors.cpf = 'CPF é obrigatório';
    } else if (formData.cpf.length !== 11) {
      newErrors.cpf = 'CPF deve ter 11 dígitos';
    }

    if (!formData.telefone.trim()) {
      newErrors.telefone = 'Telefone é obrigatório';
    } else if (formData.telefone.length < 10) {
      newErrors.telefone = 'Telefone deve ter pelo menos 10 dígitos';
    }

    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    onSubmit(formData);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {collector ? 'Editar Coletora' : 'Cadastrar Nova Coletora'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {serverError && (
            <div className="p-3 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-md">
              {serverError}
            </div>
          )}
          {/* Nome Completo */}
          <div>
            <label htmlFor="nome_completo" className="block text-sm font-medium text-gray-700 mb-1">
              Nome Completo *
            </label>
            <input
              type="text"
              id="nome_completo"
              name="nome_completo"
              value={formData.nome_completo}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.nome_completo ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Digite o nome completo"
            />
            {errors.nome_completo && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_completo}</p>
            )}
          </div>

          {/* CPF e Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="cpf" className="block text-sm font-medium text-gray-700 mb-1">
                CPF *
              </label>
              <input
                type="text"
                id="cpf"
                name="cpf"
                value={formData.cpf}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.cpf ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ex: 12345678909 (apenas números)"
                maxLength={11}
              />
              {errors.cpf && (
                <p className="mt-1 text-sm text-red-600">{errors.cpf}</p>
              )}
              {!errors.cpf && formData.cpf.length === 11 && validateCPF(formData.cpf) && (
                <p className="mt-1 text-sm text-green-600">✓ CPF válido</p>
              )}
              {!errors.cpf && formData.cpf.length < 11 && (
                <p className="mt-1 text-xs text-gray-500">
                  Digite um CPF válido com 11 dígitos (sem espaços ou pontos)
                </p>
              )}
            </div>

            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Ativo">Ativo</option>
                <option value="Inativo">Inativo</option>
                <option value="Suspenso">Suspenso</option>
                <option value="Férias">Férias</option>
              </select>
            </div>
          </div>

          {/* Telefone e Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="telefone" className="block text-sm font-medium text-gray-700 mb-1">
                Telefone *
              </label>
              <input
                type="tel"
                id="telefone"
                name="telefone"
                value={formData.telefone}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.telefone ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Digite o telefone"
              />
              {errors.telefone && (
                <p className="mt-1 text-sm text-red-600">{errors.telefone}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Digite o email"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>
          </div>

          {/* Registro Profissional e Especialização */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="registro_profissional" className="block text-sm font-medium text-gray-700 mb-1">
                Registro Profissional
              </label>
              <input
                type="text"
                id="registro_profissional"
                name="registro_profissional"
                value={formData.registro_profissional}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: COREN-SP 123456"
              />
            </div>

            <div>
              <label htmlFor="especializacao" className="block text-sm font-medium text-gray-700 mb-1">
                Especialização
              </label>
              <input
                type="text"
                id="especializacao"
                name="especializacao"
                value={formData.especializacao}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Coleta domiciliar, Pediatria"
              />
            </div>
          </div>

          {/* Data de Nascimento */}
          <div>
            <label htmlFor="data_nascimento" className="block text-sm font-medium text-gray-700 mb-1">
              Data de Nascimento
            </label>
            <input
              type="date"
              id="data_nascimento"
              name="data_nascimento"
              value={formData.data_nascimento}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Endereço */}
          <div>
            <label htmlFor="endereco" className="block text-sm font-medium text-gray-700 mb-1">
              Endereço
            </label>
            <input
              type="text"
              id="endereco"
              name="endereco"
              value={formData.endereco}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Digite o endereço completo"
            />
          </div>

          {/* Carro */}
          <div>
            <label htmlFor="carro" className="block text-sm font-medium text-gray-700 mb-1">
              Carro
            </label>
            <textarea
              id="carro"
              name="carro"
              value={formData.carro}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Informações do carro utilizado"
            />
          </div>

          {/* Observações */}
          <div>
            <label htmlFor="observacoes" className="block text-sm font-medium text-gray-700 mb-1">
              Observações
            </label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={formData.observacoes}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Observações adicionais"
            />
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Salvando...' : (collector ? 'Atualizar' : 'Cadastrar')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
