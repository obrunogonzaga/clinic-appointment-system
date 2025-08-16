import { XMarkIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useState } from 'react';
import type { DRIVER_STATUS, Driver, DriverFormData } from '../types/driver';

interface DriverFormProps {
  driver?: Driver;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DriverFormData) => void;
  isLoading?: boolean;
}

const initialFormData: DriverFormData = {
  nome_completo: '',
  cnh: '',
  telefone: '',
  email: '',
  data_nascimento: '',
  endereco: '',
  status: 'Ativo',
  carro: '',
};

export const DriverForm: React.FC<DriverFormProps> = ({
  driver,
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<DriverFormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<DriverFormData>>({});

  // Reset form when modal opens/closes or driver changes
  useEffect(() => {
    if (isOpen && driver) {
      setFormData({
        nome_completo: driver.nome_completo || '',
        cnh: driver.cnh || '',
        telefone: driver.telefone || '',
        email: driver.email || '',
        data_nascimento: driver.data_nascimento ? 
          new Date(driver.data_nascimento).toISOString().split('T')[0] : '',
        endereco: driver.endereco || '',
        status: driver.status as typeof DRIVER_STATUS[keyof typeof DRIVER_STATUS] || 'Ativo',
        carro: driver.carro || '',
      });
    } else if (isOpen && !driver) {
      setFormData(initialFormData);
    }
    setErrors({});
  }, [isOpen, driver]);

  const validateCNH = (cnh: string): boolean => {
    // Remove any non-digit characters
    const cleanCNH = cnh.replace(/\D/g, '');
    
    if (cleanCNH.length !== 11) {
      return false;
    }

    // Convert to array of numbers
    const digits = cleanCNH.split('').map(Number);

    // First verification digit
    let sum1 = 0;
    for (let i = 0; i < 9; i++) {
      sum1 += digits[i] * (9 - i);
    }
    const remainder1 = sum1 % 11;
    const firstDigit = remainder1 < 2 ? 0 : 11 - remainder1;

    if (digits[9] !== firstDigit) {
      return false;
    }

    // Second verification digit
    // Official CNH algorithm: multiply by sequence (1,2,3,4,5,6,7,8,9,1)
    const multipliers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1];
    let sum2 = 0;
    for (let i = 0; i < 10; i++) {
      sum2 += digits[i] * multipliers[i];
    }
    const remainder2 = sum2 % 11;
    const secondDigit = remainder2 < 2 ? 0 : 11 - remainder2;

    return digits[10] === secondDigit;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    
    // For CNH, only allow numbers
    if (name === 'cnh') {
      const cleanValue = value.replace(/\D/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: cleanValue
      }));
      
      // Real-time CNH validation
      if (cleanValue.length === 11) {
        if (!validateCNH(cleanValue)) {
          setErrors(prev => ({
            ...prev,
            cnh: 'CNH inválida. Verifique os dígitos.'
          }));
        } else {
          setErrors(prev => ({
            ...prev,
            cnh: undefined
          }));
        }
      } else if (cleanValue.length > 0) {
        setErrors(prev => ({
          ...prev,
          cnh: undefined
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear error when user starts typing (except for CNH which has its own validation)
    if (name !== 'cnh' && errors[name as keyof DriverFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<DriverFormData> = {};

    if (!formData.nome_completo.trim()) {
      newErrors.nome_completo = 'Nome completo é obrigatório';
    }

    if (!formData.cnh.trim()) {
      newErrors.cnh = 'CNH é obrigatória';
    } else if (formData.cnh.length !== 11) {
      newErrors.cnh = 'CNH deve ter 11 dígitos';
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
            {driver ? 'Editar Motorista' : 'Cadastrar Novo Motorista'}
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

          {/* CNH e Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="cnh" className="block text-sm font-medium text-gray-700 mb-1">
                CNH *
              </label>
              <input
                type="text"
                id="cnh"
                name="cnh"
                value={formData.cnh}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.cnh ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ex: 12345678908 (apenas números)"
                maxLength={11}
              />
              {errors.cnh && (
                <p className="mt-1 text-sm text-red-600">{errors.cnh}</p>
              )}
              {!errors.cnh && formData.cnh.length === 11 && validateCNH(formData.cnh) && (
                <p className="mt-1 text-sm text-green-600">✓ CNH válida</p>
              )}
              {!errors.cnh && formData.cnh.length < 11 && (
                <p className="mt-1 text-xs text-gray-500">
                  Digite uma CNH válida com 11 dígitos (sem espaços ou pontos)
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
              {isLoading ? 'Salvando...' : (driver ? 'Atualizar' : 'Cadastrar')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};