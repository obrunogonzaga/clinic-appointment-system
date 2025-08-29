import { XMarkIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useState } from 'react';
import type { CAR_STATUS, Car, CarFormData } from '../types/car';

interface CarFormProps {
  car?: Car;
  onSubmit: (data: CarFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const initialFormData: CarFormData = {
  nome: '',
  unidade: '',
  placa: '',
  modelo: '',
  cor: '',
  status: 'Ativo',
  observacoes: '',
};

export const CarForm: React.FC<CarFormProps> = ({
  car,
  onSubmit,
  onCancel,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<CarFormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<CarFormData>>({});

  // Reset form when car changes
  useEffect(() => {
    if (car) {
      setFormData({
        nome: car.nome || '',
        unidade: car.unidade || '',
        placa: car.placa || '',
        modelo: car.modelo || '',
        cor: car.cor || '',
        status: car.status as typeof CAR_STATUS[keyof typeof CAR_STATUS] || 'Ativo',
        observacoes: car.observacoes || '',
      });
    } else {
      setFormData(initialFormData);
    }
    setErrors({});
  }, [car]);

  const validatePlaca = (placa: string): boolean => {
    if (!placa) return true; // Optional field

    // Remove spaces and hyphens
    const cleanPlaca = placa.replace(/[-\s]/g, '').toUpperCase();
    
    // Brazilian license plate patterns:
    // Old format: ABC1234 (3 letters + 4 numbers)
    // Mercosul format: ABC1D23 (3 letters + 1 number + 1 letter + 2 numbers)
    const oldPattern = /^[A-Z]{3}\d{4}$/;
    const mercosulPattern = /^[A-Z]{3}\d[A-Z]\d{2}$/;
    
    return oldPattern.test(cleanPlaca) || mercosulPattern.test(cleanPlaca);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    
    // For placa, format as uppercase and remove invalid characters
    if (name === 'placa') {
      const formattedValue = value.toUpperCase().replace(/[^A-Z0-9-]/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: formattedValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear field error when user starts typing
    if (errors[name as keyof CarFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<CarFormData> = {};

    // Required fields
    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formData.unidade.trim()) {
      newErrors.unidade = 'Unidade é obrigatória';
    }

    // Placa validation (optional but must be valid if provided)
    if (formData.placa && !validatePlaca(formData.placa)) {
      newErrors.placa = 'Placa deve estar no formato brasileiro (ABC1234 ou ABC1D23)';
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {car ? 'Editar Carro' : 'Novo Carro'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isLoading}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Nome */}
            <div>
              <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-1">
                Nome do Carro <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="nome"
                name="nome"
                value={formData.nome}
                onChange={handleInputChange}
                placeholder="Ex: CENTER 3 CARRO 1"
                disabled={isLoading}
                className={`w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500 ${
                           errors.nome ? 'border-red-300' : 'border-gray-300'
                         }`}
              />
              {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
            </div>

            {/* Unidade */}
            <div>
              <label htmlFor="unidade" className="block text-sm font-medium text-gray-700 mb-1">
                Unidade <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="unidade"
                name="unidade"
                value={formData.unidade}
                onChange={handleInputChange}
                placeholder="Ex: UND84"
                disabled={isLoading}
                className={`w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500 ${
                           errors.unidade ? 'border-red-300' : 'border-gray-300'
                         }`}
              />
              {errors.unidade && <p className="mt-1 text-sm text-red-600">{errors.unidade}</p>}
            </div>

            {/* Placa */}
            <div>
              <label htmlFor="placa" className="block text-sm font-medium text-gray-700 mb-1">
                Placa
              </label>
              <input
                type="text"
                id="placa"
                name="placa"
                value={formData.placa}
                onChange={handleInputChange}
                placeholder="ABC-1234 ou ABC1D23"
                disabled={isLoading}
                maxLength={8}
                className={`w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500 ${
                           errors.placa ? 'border-red-300' : 'border-gray-300'
                         }`}
              />
              {errors.placa && <p className="mt-1 text-sm text-red-600">{errors.placa}</p>}
            </div>

            {/* Modelo */}
            <div>
              <label htmlFor="modelo" className="block text-sm font-medium text-gray-700 mb-1">
                Modelo
              </label>
              <input
                type="text"
                id="modelo"
                name="modelo"
                value={formData.modelo}
                onChange={handleInputChange}
                placeholder="Ex: Honda Civic"
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500"
              />
            </div>

            {/* Cor */}
            <div>
              <label htmlFor="cor" className="block text-sm font-medium text-gray-700 mb-1">
                Cor
              </label>
              <input
                type="text"
                id="cor"
                name="cor"
                value={formData.cor}
                onChange={handleInputChange}
                placeholder="Ex: Branco"
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500"
              />
            </div>

            {/* Status */}
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm 
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-50 disabled:text-gray-500"
              >
                <option value="Ativo">Ativo</option>
                <option value="Inativo">Inativo</option>
                <option value="Manutenção">Manutenção</option>
                <option value="Vendido">Vendido</option>
              </select>
            </div>
          </div>

          {/* Observações */}
          <div className="mt-6">
            <label htmlFor="observacoes" className="block text-sm font-medium text-gray-700 mb-1">
              Observações
            </label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={formData.observacoes}
              onChange={handleInputChange}
              rows={3}
              placeholder="Observações adicionais sobre o carro..."
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       disabled:bg-gray-50 disabled:text-gray-500 resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 
                       rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 
                       focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent 
                       rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 
                       focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center"
            >
              {isLoading && (
                <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {car ? 'Salvar Alterações' : 'Criar Carro'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};