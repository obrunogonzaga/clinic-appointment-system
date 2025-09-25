import React from 'react';
import { AppointmentCard } from './AppointmentCard';
import type { AppointmentViewModel } from '../types/appointment';
import type { ActiveDriver } from '../types/driver';
import type { ActiveCollector } from '../types/collector';
import type { LogisticsPackage } from '../types/logistics-package';
import { useResponsiveLayout } from '../hooks/useResponsiveLayout';

interface AppointmentCardListProps {
  appointments: AppointmentViewModel[];
  drivers: ActiveDriver[];
  collectors?: ActiveCollector[];
  logisticsPackages?: LogisticsPackage[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onLogisticsPackageChange?: (
    appointmentId: string,
    logisticsPackageId: string | null,
  ) => void;
  onDelete?: (id: string) => void;
  onSelect?: (id: string) => void;
  isReadOnly?: boolean;
}

const CardSkeleton: React.FC = () => (
  <div className="bg-white border border-gray-200 rounded-lg p-4 animate-pulse">
    <div className="flex justify-between items-start mb-3">
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-6 bg-gray-200 rounded w-20"></div>
    </div>
    <div className="space-y-2">
      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
      <div className="h-3 bg-gray-200 rounded w-2/3"></div>
    </div>
    <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
      <div className="h-8 bg-gray-200 rounded w-32"></div>
      <div className="h-6 w-6 bg-gray-200 rounded"></div>
    </div>
  </div>
);

export const AppointmentCardList: React.FC<AppointmentCardListProps> = ({
  appointments,
  drivers,
  collectors = [],
  logisticsPackages = [],
  isLoading = false,
  onStatusChange,
  onLogisticsPackageChange,
  onDelete,
  onSelect,
  isReadOnly = false,
}) => {
  const { isMobile } = useResponsiveLayout();

  // Determine grid columns based on screen size
  const getGridColumns = () => {
    if (isMobile) {
      return 'grid-cols-1';
    }

    return 'grid-cols-2';
  };

  if (isLoading) {
    return (
      <div className={`grid ${getGridColumns()} gap-4`}>
        {Array.from({ length: 6 }, (_, index) => (
          <CardSkeleton key={`skeleton-loading-${index}`} />
        ))}
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg mb-2">
          Nenhum agendamento encontrado
        </div>
        <div className="text-gray-400 text-sm">
          Faça upload de um arquivo Excel ou ajuste os filtros
        </div>
      </div>
    );
  }

  return (
    <div className={`grid ${getGridColumns()} gap-4`}>
      {appointments.map((appointment) => (
        <AppointmentCard
          key={appointment.id}
          appointment={appointment}
          drivers={drivers}
          collectors={collectors}
          logisticsPackages={logisticsPackages}
          onStatusChange={onStatusChange}
          onLogisticsPackageChange={onLogisticsPackageChange}
          onDelete={onDelete}
          compact={isMobile}
          onSelect={onSelect}
          isReadOnly={isReadOnly}
        />
      ))}
    </div>
  );
};
