import {
    CheckCircleIcon,
    PlusIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline';
import { isAxiosError } from 'axios';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AppointmentCardList } from '../components/AppointmentCardList';
import { AppointmentCalendarView } from '../components/AppointmentCalendarView';
import { AppointmentFormModal } from '../components/AppointmentFormModal';
import { AppointmentDetailsModal } from '../components/AppointmentDetailsModal';
import { AppointmentFilters } from '../components/AppointmentFilters';
import { CollectorAgendaView } from '../components/CollectorAgendaView';
import { FileUpload } from '../components/FileUpload';
import { ToastContainer } from '../components/ui/Toast';
import { ViewModeToggle, type ViewMode } from '../components/ViewModeToggle';
import { AppointmentTable } from '../components/AppointmentTable';
import { AppointmentKpiCards } from '../components/AppointmentKpiCards';
import { appointmentAPI, collectorAPI, driverAPI, logisticsPackageAPI, tagAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import type {
  AppointmentCreateRequest,
  AppointmentFilter,
  ExcelUploadResponse
} from '../types/appointment';
import {
  countAppointmentsByStatus,
  filterAppointmentsByDateRange,
  filterAppointmentsBySearch,
  getDateRangeForShortcut,
  toAppointmentViewModel,
  type DateRange,
  type DateShortcut,
} from '../utils/appointmentViewModel';
import { parseLocalDateFromInput } from '../utils/dateUtils';

export const AppointmentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { toasts, success: showToastSuccess, error: showToastError, removeToast } = useToast();
  
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedAppointmentId = searchParams.get('itemId');

  const [filters, setFilters] = useState<AppointmentFilter>({
    page: 1,
    page_size: 50
  });
  const [uploadResult, setUploadResult] = useState<ExcelUploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('cards');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateShortcut, setDateShortcut] = useState<DateShortcut | null>(null);
  const [currentCalendarDate, setCurrentCalendarDate] = useState<Date>(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreatingAppointment, setIsCreatingAppointment] = useState(false);
  const [selectedAgendaDate, setSelectedAgendaDate] = useState<Date>(new Date());

  // Fetch appointments
  const { 
    data: appointmentsData, 
    isLoading: isLoadingAppointments
  } = useQuery({
    queryKey: ['appointments', filters],
    queryFn: () => appointmentAPI.getAppointments(filters),
    refetchOnWindowFocus: false,
  });

  // Fetch filter options
  const { 
    data: filterOptions, 
    isLoading: isLoadingFilters 
  } = useQuery({
    queryKey: ['filterOptions'],
    queryFn: () => appointmentAPI.getFilterOptions(),
    refetchOnWindowFocus: false,
  });

  // Fetch active drivers
  const { data: driversData } = useQuery({
    queryKey: ['activeDrivers'],
    queryFn: () => driverAPI.getActiveDrivers(),
    refetchOnWindowFocus: false,
  });

  // Fetch active collectors
  const { data: collectorsData } = useQuery({
    queryKey: ['activeCollectors'],
    queryFn: () => collectorAPI.getActiveCollectors(),
    refetchOnWindowFocus: false,
  });

  const { data: logisticsPackagesData } = useQuery({
    queryKey: ['activeLogisticsPackages'],
    queryFn: () => logisticsPackageAPI.listActivePackages(),
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });

  const { data: tagsData } = useQuery({
    queryKey: ['activeTags'],
    queryFn: () => tagAPI.listTags({ page: 1, page_size: 100, include_inactive: false }),
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });

  const maxTagsPerAppointment = filterOptions?.max_tags_per_appointment ?? 5;

  const openAppointmentDetails = (appointmentId: string) => {
    const next = new URLSearchParams(searchParams);
    next.set('itemId', appointmentId);
    setSearchParams(next, { replace: false });
  };

  const closeAppointmentDetails = () => {
    const next = new URLSearchParams(searchParams);
    next.delete('itemId');
    setSearchParams(next, { replace: false });
  };

  const handleUploadSuccess = (result: ExcelUploadResponse) => {
    setUploadResult(result);
    setUploadError(null);
    
    // Refresh data after successful upload
    queryClient.invalidateQueries({ queryKey: ['appointments'] });
    queryClient.invalidateQueries({ queryKey: ['filterOptions'] });
    queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    
    // Auto-hide success message after 50 seconds
    setTimeout(() => {
      setUploadResult(null);
    }, 50000);
  };

  const handleUploadError = (error: string) => {
    setUploadError(error);
    setUploadResult(null);
    
    // Auto-hide error message after 5 seconds
    setTimeout(() => {
      setUploadError(null);
    }, 5000);
  };

  const handleCreateAppointment = async (formData: AppointmentCreateRequest) => {
    try {
      setIsCreatingAppointment(true);
      const response = await appointmentAPI.createAppointment(formData);

      showToastSuccess(response.message || 'Agendamento criado com sucesso');
      setIsCreateModalOpen(false);

      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['filterOptions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      const fallbackMessage = 'Não foi possível criar o agendamento.';
      if (isAxiosError(error)) {
        const data = error.response?.data as { message?: string; detail?: string } | undefined;
        showToastError(data?.message || data?.detail || fallbackMessage);
      } else {
        showToastError(fallbackMessage);
      }
    } finally {
      setIsCreatingAppointment(false);
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await appointmentAPI.updateAppointmentStatus(id, status);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      console.error('Error updating appointment status:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este agendamento?')) {
      return;
    }

    try {
      await appointmentAPI.deleteAppointment(id);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      console.error('Error deleting appointment:', error);
    }
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const dateRange = useMemo<DateRange | null>(() => {
    if (filters.data) {
      // Parse as local date to avoid timezone shift from Date('yyyy-MM-dd')
      const localDate = parseLocalDateFromInput(filters.data);
      if (localDate && !Number.isNaN(localDate.getTime())) {
        const start = new Date(
          localDate.getFullYear(),
          localDate.getMonth(),
          localDate.getDate(),
          0,
          0,
          0,
          0
        );
        const end = new Date(
          localDate.getFullYear(),
          localDate.getMonth(),
          localDate.getDate(),
          23,
          59,
          59,
          999
        );
        return { start, end };
      }
    }

    return dateShortcut ? getDateRangeForShortcut(dateShortcut) : null;
  }, [filters.data, dateShortcut]);

  const appointmentsViewModel = useMemo(() => {
    return (appointmentsData?.appointments || []).map(toAppointmentViewModel);
  }, [appointmentsData?.appointments]);

  const appointmentsAfterDate = useMemo(
    () => filterAppointmentsByDateRange(appointmentsViewModel, dateRange),
    [appointmentsViewModel, dateRange]
  );

  const filteredAppointments = useMemo(
    () => filterAppointmentsBySearch(appointmentsAfterDate, searchTerm),
    [appointmentsAfterDate, searchTerm]
  );

  const kpiStats = useMemo(
    () => countAppointmentsByStatus(filteredAppointments),
    [filteredAppointments]
  );

  const handleDriverChange = async (appointmentId: string, driverId: string) => {
    try {
      await appointmentAPI.updateAppointmentDriver(appointmentId, driverId);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    } catch (error) {
      console.error('Error updating appointment driver:', error);
    }
  };

  const handleCollectorChange = async (appointmentId: string, collectorId: string) => {
    try {
      await appointmentAPI.updateAppointmentCollector(appointmentId, collectorId);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    } catch (error) {
      console.error('Error updating appointment collector:', error);
    }
  };

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <AppointmentFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateAppointment}
        isSubmitting={isCreatingAppointment}
        brands={filterOptions?.brands || []}
        units={filterOptions?.units || []}
        statuses={filterOptions?.statuses}
        drivers={driversData?.drivers || []}
        collectors={collectorsData?.collectors || []}
        tags={tagsData?.data ?? []}
        maxTags={maxTagsPerAppointment}
        logisticsPackages={logisticsPackagesData?.data ?? []}
      />

      <AppointmentDetailsModal
        isOpen={Boolean(selectedAppointmentId)}
        appointmentId={selectedAppointmentId}
        onClose={closeAppointmentDetails}
        drivers={driversData?.drivers || []}
        collectors={collectorsData?.collectors || []}
        statuses={filterOptions?.statuses}
        tags={tagsData?.data ?? []}
        maxTags={maxTagsPerAppointment}
        onEditSuccess={showToastSuccess}
        onEditError={showToastError}
        logisticsPackages={logisticsPackagesData?.data ?? []}
      />

      <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900">
            Gerenciamento de Agendamentos
          </h1>
          <p className="mt-2 text-gray-500">
            Faça upload de arquivos Excel e gerencie agendamentos
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60"
            disabled={isCreatingAppointment}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Adicionar Agendamento
          </button>
          <div className="flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 shadow-sm">
            <span className="text-sm font-medium text-gray-600">Mostrar:</span>
            <ViewModeToggle
              viewMode={viewMode}
              onViewChange={setViewMode}
              variant="minimal"
              className="gap-1"
            />
          </div>
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>
      </div>

      {(uploadResult || uploadError) && (
        <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          {uploadResult && (
            <div className="flex flex-col gap-2 text-sm text-green-700 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                <span className="font-medium">{uploadResult.message}</span>
              </div>
              <div className="flex flex-wrap gap-x-3 gap-y-1 text-green-600">
                <span>Total: {uploadResult.total_rows}</span>
                <span>Válidos: {uploadResult.valid_rows}</span>
                <span>Inválidos: {uploadResult.invalid_rows}</span>
                <span>Importados: {uploadResult.imported_appointments}</span>
                {uploadResult.duplicates_found > 0 && (
                  <span>Duplicados: {uploadResult.duplicates_found}</span>
                )}
                {uploadResult.processing_time && (
                  <span>Tempo: {uploadResult.processing_time.toFixed(1)}s</span>
                )}
              </div>
            </div>
          )}

          {uploadError && (
            <div className="flex items-center gap-2 text-sm text-red-700">
              <XCircleIcon className="h-5 w-5 text-red-500" />
              <span className="font-medium">{uploadError}</span>
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <AppointmentFilters
        filters={filters}
        onFiltersChange={setFilters}
        units={filterOptions?.units || []}
        brands={filterOptions?.brands || []}
        statuses={filterOptions?.statuses || []}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        dateShortcut={dateShortcut}
        onDateShortcutChange={setDateShortcut}
        isLoading={isLoadingFilters}
      />

      {/* KPIs */}
      <AppointmentKpiCards
        total={kpiStats.total}
        confirmed={kpiStats.confirmed}
        pendingOrCancelled={kpiStats.pendingOrCancelled}
        isLoading={isLoadingAppointments}
      />

      {/* Appointments Display */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Agendamentos
              {viewMode === 'calendar' && (
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Visualização Calendário)
                </span>
              )}
              {viewMode === 'agenda' && (
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Agenda das Coletoras)
                </span>
              )}
            </h2>
            
            {appointmentsData?.pagination && (
              <div className="text-sm text-gray-500">
                Mostrando {filteredAppointments.length} de {appointmentsData.pagination.total_items} agendamentos
              </div>
            )}
          </div>

          {/* Render content based on view mode */}
          {viewMode === 'cards' && (
            <AppointmentCardList
              appointments={filteredAppointments}
              drivers={driversData?.drivers || []}
              collectors={collectorsData?.collectors || []}
              isLoading={isLoadingAppointments}
              onStatusChange={handleStatusChange}
              onDriverChange={handleDriverChange}
              onCollectorChange={handleCollectorChange}
              onDelete={handleDelete}
              onSelect={openAppointmentDetails}
            />
          )}

          {viewMode === 'table' && (
            <AppointmentTable
              appointments={filteredAppointments}
              drivers={driversData?.drivers || []}
              collectors={collectorsData?.collectors || []}
              isLoading={isLoadingAppointments}
              onStatusChange={handleStatusChange}
              onDriverChange={handleDriverChange}
              onCollectorChange={handleCollectorChange}
              onDelete={handleDelete}
              onSelect={openAppointmentDetails}
            />
          )}

          {viewMode === 'calendar' && (
            <AppointmentCalendarView
              appointments={filteredAppointments}
              currentDate={currentCalendarDate}
              selectedDate={selectedDate}
              onDateSelect={setSelectedDate}
              onMonthChange={setCurrentCalendarDate}
              onAppointmentStatusChange={handleStatusChange}
              onAppointmentDriverChange={handleDriverChange}
              onAppointmentCollectorChange={handleCollectorChange}
              onAppointmentDelete={handleDelete}
              drivers={driversData?.drivers || []}
              collectors={collectorsData?.collectors || []}
              isLoading={isLoadingAppointments}
            />
          )}

          {viewMode === 'agenda' && (
            <div className="space-y-4">
              {/* Date Selector for Agenda */}
              <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center space-x-4">
                  <label htmlFor="agenda-date" className="text-sm font-medium text-gray-700">
                    Data da Agenda:
                  </label>
                  <input
                    id="agenda-date"
                    type="date"
                    value={selectedAgendaDate.toISOString().split('T')[0]}
                    onChange={(e) => setSelectedAgendaDate(new Date(e.target.value))}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <CollectorAgendaView
                appointments={filteredAppointments}
                collectors={collectorsData?.collectors || []}
                drivers={driversData?.drivers || []}
                selectedDate={selectedAgendaDate}
                isLoading={isLoadingAppointments}
                onAppointmentStatusChange={handleStatusChange}
                onAppointmentDriverChange={handleDriverChange}
                onAppointmentCollectorChange={handleCollectorChange}
                onAppointmentDelete={handleDelete}
                onDateChange={setSelectedAgendaDate}
              />
            </div>
          )}

          {/* Pagination - only show for cards view */}
          {viewMode !== 'calendar' && appointmentsData?.pagination && appointmentsData.pagination.total_pages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-500">
                Página {appointmentsData.pagination.page} de {appointmentsData.pagination.total_pages}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => handlePageChange(appointmentsData.pagination.page - 1)}
                  disabled={!appointmentsData.pagination.has_previous}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                
                <button
                  onClick={() => handlePageChange(appointmentsData.pagination.page + 1)}
                  disabled={!appointmentsData.pagination.has_next}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Próximo
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
};
