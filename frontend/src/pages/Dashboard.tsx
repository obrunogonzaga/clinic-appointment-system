import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CalendarDaysIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  BuildingOfficeIcon,
  TagIcon,
  TruckIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { appointmentAPI, driverAPI } from '../services/api';

interface DashboardProps {
  onTabChange?: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onTabChange }) => {
  // Fetch dashboard stats
  const { 
    data: dashboardStats, 
    isLoading: isLoadingStats 
  } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => appointmentAPI.getDashboardStats(),
    refetchOnWindowFocus: false,
  });

  // Fetch driver stats
  const { 
    data: driverStats, 
    isLoading: isLoadingDriverStats 
  } = useQuery({
    queryKey: ['driverStats'],
    queryFn: () => driverAPI.getDriverStats(),
    refetchOnWindowFocus: false,
  });

  const stats = dashboardStats?.stats || {
    total_appointments: 0,
    confirmed_appointments: 0,
    cancelled_appointments: 0,
    total_units: 0,
    total_brands: 0
  };

  const drivers = driverStats?.stats || {
    total_drivers: 0,
    active_drivers: 0,
    inactive_drivers: 0,
    suspended_drivers: 0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Visão geral do sistema de agendamentos
        </p>
      </div>

      {/* Appointments Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Estatísticas de Agendamentos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CalendarDaysIcon className="w-10 h-10 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CheckCircleIcon className="w-10 h-10 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Confirmados</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.confirmed_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Cancelados</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.cancelled_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <BuildingOfficeIcon className="w-10 h-10 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Unidades</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_units}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <TagIcon className="w-10 h-10 text-indigo-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Marcas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_brands}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Driver Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Estatísticas de Motoristas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <UserGroupIcon className="w-10 h-10 text-gray-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingDriverStats ? '...' : drivers.total_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <TruckIcon className="w-10 h-10 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingDriverStats ? '...' : drivers.active_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Inativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingDriverStats ? '...' : drivers.inactive_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Suspensos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingDriverStats ? '...' : drivers.suspended_drivers}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Ações Rápidas</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => onTabChange?.('appointments')}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <CalendarDaysIcon className="w-8 h-8 text-blue-600 mb-2" />
            <h3 className="font-medium text-gray-900">Gerenciar Agendamentos</h3>
            <p className="text-sm text-gray-600">Visualizar, editar e fazer upload de novos agendamentos</p>
          </button>

          <button
            onClick={() => onTabChange?.('drivers')}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <TruckIcon className="w-8 h-8 text-green-600 mb-2" />
            <h3 className="font-medium text-gray-900">Cadastrar Motoristas</h3>
            <p className="text-sm text-gray-600">Adicionar novos motoristas e gerenciar dados existentes</p>
          </button>

          <button
            onClick={() => alert('Funcionalidade de relatórios será implementada em breve!')}
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <BuildingOfficeIcon className="w-8 h-8 text-purple-600 mb-2" />
            <h3 className="font-medium text-gray-900">Relatórios</h3>
            <p className="text-sm text-gray-600">Gerar relatórios de agendamentos e motoristas</p>
          </button>
        </div>
      </div>
    </div>
  );
};