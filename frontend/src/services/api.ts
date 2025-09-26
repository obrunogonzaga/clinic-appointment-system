import axios from 'axios';
import type {
    AppointmentFilter,
    AppointmentListResponse,
    DashboardStats,
    ExcelUploadResponse,
    FilterOptions
} from '../types/appointment';
import type {
    ActiveCollectorListResponse,
    CollectorCreateRequest,
    CollectorFilter,
    CollectorFilterOptions,
    CollectorListResponse,
    CollectorResponse,
    CollectorStats,
    CollectorUpdateRequest
} from '../types/collector';
import type {
    ActiveDriverListResponse,
    DriverCreateRequest,
    DriverFilter,
    DriverFilterOptions,
    DriverListResponse,
    DriverResponse,
    DriverStats,
    DriverUpdateRequest
} from '../types/driver';
import type {
    ActiveCarListResponse,
    CarCreateRequest,
    CarFilter,
    CarFilterOptions,
    CarFromStringRequest,
    CarFromStringResponse,
    CarListResponse,
    CarResponse,
    CarStats,
    CarUpdateRequest
} from '../types/car';
import type {
    ApiDataResponse,
    ConfirmUploadRequest,
    DownloadUrlPayload,
    PatientDocument,
    PatientDocumentList,
    PresignUploadRequest,
    PresignUploadResponse,
} from '../types/patientDocument';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const defaultUserId = import.meta.env.VITE_API_USER_ID ?? 'dev-user';
const defaultUserRole = import.meta.env.VITE_API_USER_ROLE ?? 'admin';
const defaultTenantId = import.meta.env.VITE_API_TENANT_ID ?? 'default';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-User-Id': defaultUserId,
    'X-User-Role': defaultUserRole,
    'X-Tenant-Id': defaultTenantId,
  },
});

// Request interceptor for adding auth headers in the future
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const appointmentAPI = {
  // Upload Excel file
  uploadExcel: async (file: File, replaceExisting = false): Promise<ExcelUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<ExcelUploadResponse>(
      `/appointments/upload?replace_existing=${replaceExisting}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000, // 3 minutes timeout for Excel upload with address normalization
      }
    );
    
    return response.data;
  },

  // Get appointments with filters
  getAppointments: async (filters: AppointmentFilter): Promise<AppointmentListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.nome_unidade) params.append('nome_unidade', filters.nome_unidade);
    if (filters.nome_marca) params.append('nome_marca', filters.nome_marca);
    if (filters.data) params.append('data', filters.data);
    if (filters.status) params.append('status', filters.status);
    if (filters.driver_id) params.append('driver_id', filters.driver_id);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const response = await api.get<AppointmentListResponse>(
      `/appointments/?${params.toString()}`
    );
    
    return response.data;
  },

  // Get filter options
  getFilterOptions: async (): Promise<FilterOptions> => {
    const response = await api.get<FilterOptions>('/appointments/filter-options');
    return response.data;
  },

  // Get dashboard statistics
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/appointments/stats');
    return response.data;
  },

  // Update appointment status
  updateAppointmentStatus: async (id: string, status: string): Promise<void> => {
    await api.put(`/appointments/${id}/status?new_status=${status}`);
  },

  // Delete appointment
  deleteAppointment: async (id: string): Promise<void> => {
    await api.delete(`/appointments/${id}`);
  },

  // Update appointment driver
  updateAppointmentDriver: async (appointmentId: string, driverId: string): Promise<void> => {
    await api.put(`/appointments/${appointmentId}`, {
      driver_id: driverId || null
    });
  },

  // Update appointment collector
  updateAppointmentCollector: async (appointmentId: string, collectorId: string): Promise<void> => {
    await api.put(`/appointments/${appointmentId}/collector?collector_id=${collectorId || ''}`);
  },

  // Patient document helpers
  getAppointmentDocuments: async (appointmentId: string): Promise<PatientDocumentList> => {
    const response = await api.get<ApiDataResponse<PatientDocumentList>>(
      `/appointments/${appointmentId}/documents`
    );
    return response.data.data;
  },

  presignDocumentUpload: async (
    appointmentId: string,
    payload: PresignUploadRequest,
  ): Promise<PresignUploadResponse> => {
    const response = await api.post<ApiDataResponse<PresignUploadResponse>>(
      `/appointments/${appointmentId}/documents/presign`,
      payload,
    );
    return response.data.data;
  },

  confirmDocumentUpload: async (
    appointmentId: string,
    documentId: string,
    payload: ConfirmUploadRequest,
  ): Promise<PatientDocument> => {
    const response = await api.post<ApiDataResponse<PatientDocument>>(
      `/appointments/${appointmentId}/documents/${documentId}/confirm`,
      payload,
    );
    return response.data.data;
  },

  getDocumentDownloadUrl: async (
    appointmentId: string,
    documentId: string,
  ): Promise<DownloadUrlPayload> => {
    const response = await api.get<ApiDataResponse<DownloadUrlPayload>>(
      `/appointments/${appointmentId}/documents/${documentId}/download`
    );
    return response.data.data;
  },

  deleteDocument: async (
    appointmentId: string,
    documentId: string,
    hard = false,
  ): Promise<PatientDocument> => {
    const response = await api.delete<ApiDataResponse<PatientDocument>>(
      `/appointments/${appointmentId}/documents/${documentId}?hard=${hard}`
    );
    return response.data.data;
  },
};

export const driverAPI = {
  // Create driver
  createDriver: async (data: DriverCreateRequest): Promise<DriverResponse> => {
    const response = await api.post<DriverResponse>('/drivers', data);
    return response.data;
  },

  // Get drivers with filters
  getDrivers: async (filters: DriverFilter): Promise<DriverListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.nome_completo) params.append('nome_completo', filters.nome_completo);
    if (filters.cnh) params.append('cnh', filters.cnh);
    if (filters.telefone) params.append('telefone', filters.telefone);
    if (filters.email) params.append('email', filters.email);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const response = await api.get<DriverListResponse>(
      `/drivers?${params.toString()}`
    );
    
    return response.data;
  },

  // Get driver by ID
  getDriver: async (id: string): Promise<DriverResponse> => {
    const response = await api.get<DriverResponse>(`/drivers/${id}`);
    return response.data;
  },

  // Update driver
  updateDriver: async (id: string, data: DriverUpdateRequest): Promise<DriverResponse> => {
    const response = await api.put<DriverResponse>(`/drivers/${id}`, data);
    return response.data;
  },

  // Delete driver
  deleteDriver: async (id: string): Promise<void> => {
    await api.delete(`/drivers/${id}`);
  },

  // Update driver status
  updateDriverStatus: async (id: string, status: string): Promise<DriverResponse> => {
    const response = await api.put<DriverResponse>(`/drivers/${id}/status?new_status=${status}`);
    return response.data;
  },

  // Get active drivers
  getActiveDrivers: async (): Promise<ActiveDriverListResponse> => {
    const response = await api.get<ActiveDriverListResponse>('/drivers/active');
    return response.data;
  },

  // Get driver statistics
  getDriverStats: async (): Promise<DriverStats> => {
    const response = await api.get<DriverStats>('/drivers/stats');
    return response.data;
  },

  // Get driver filter options
  getDriverFilterOptions: async (): Promise<DriverFilterOptions> => {
    const response = await api.get<DriverFilterOptions>('/drivers/filter-options');
    return response.data;
  },
};

export const collectorAPI = {
  // Create collector
  createCollector: async (data: CollectorCreateRequest): Promise<CollectorResponse> => {
    const response = await api.post<CollectorResponse>('/collectors', data);
    return response.data;
  },

  // Get collectors with filters
  getCollectors: async (filters: CollectorFilter): Promise<CollectorListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.nome_completo) params.append('nome_completo', filters.nome_completo);
    if (filters.cpf) params.append('cpf', filters.cpf);
    if (filters.telefone) params.append('telefone', filters.telefone);
    if (filters.email) params.append('email', filters.email);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const response = await api.get<CollectorListResponse>(
      `/collectors?${params.toString()}`
    );
    
    return response.data;
  },

  // Get collector by ID
  getCollector: async (id: string): Promise<CollectorResponse> => {
    const response = await api.get<CollectorResponse>(`/collectors/${id}`);
    return response.data;
  },

  // Update collector
  updateCollector: async (id: string, data: CollectorUpdateRequest): Promise<CollectorResponse> => {
    const response = await api.put<CollectorResponse>(`/collectors/${id}`, data);
    return response.data;
  },

  // Delete collector
  deleteCollector: async (id: string): Promise<void> => {
    await api.delete(`/collectors/${id}`);
  },

  // Update collector status
  updateCollectorStatus: async (id: string, status: string): Promise<CollectorResponse> => {
    const response = await api.put<CollectorResponse>(`/collectors/${id}/status?new_status=${status}`);
    return response.data;
  },

  // Get active collectors
  getActiveCollectors: async (): Promise<ActiveCollectorListResponse> => {
    const response = await api.get<ActiveCollectorListResponse>('/collectors/active');
    return response.data;
  },

  // Get collector statistics
  getCollectorStats: async (): Promise<CollectorStats> => {
    const response = await api.get<CollectorStats>('/collectors/stats');
    return response.data;
  },

  // Get collector filter options
  getCollectorFilterOptions: async (): Promise<CollectorFilterOptions> => {
    const response = await api.get<CollectorFilterOptions>('/collectors/filter-options');
    return response.data;
  },
};

export const carAPI = {
  // Create car
  createCar: async (data: CarCreateRequest): Promise<CarResponse> => {
    const response = await api.post<CarResponse>('/cars', data);
    return response.data;
  },

  // Get cars with filters
  getCars: async (filters: CarFilter): Promise<CarListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.nome) params.append('nome', filters.nome);
    if (filters.unidade) params.append('unidade', filters.unidade);
    if (filters.placa) params.append('placa', filters.placa);
    if (filters.modelo) params.append('modelo', filters.modelo);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const response = await api.get<CarListResponse>(
      `/cars?${params.toString()}`
    );
    
    return response.data;
  },

  // Get car by ID
  getCar: async (id: string): Promise<CarResponse> => {
    const response = await api.get<CarResponse>(`/cars/${id}`);
    return response.data;
  },

  // Update car
  updateCar: async (id: string, data: CarUpdateRequest): Promise<CarResponse> => {
    const response = await api.put<CarResponse>(`/cars/${id}`, data);
    return response.data;
  },

  // Delete car
  deleteCar: async (id: string): Promise<void> => {
    await api.delete(`/cars/${id}`);
  },

  // Get active cars
  getActiveCars: async (): Promise<ActiveCarListResponse> => {
    const response = await api.get<ActiveCarListResponse>('/cars/active/list');
    return response.data;
  },

  // Get car statistics
  getCarStats: async (): Promise<CarStats> => {
    const response = await api.get<CarStats>('/cars/statistics/overview');
    return response.data;
  },

  // Get car filter options
  getCarFilterOptions: async (): Promise<CarFilterOptions> => {
    const response = await api.get<CarFilterOptions>('/cars/filters/options');
    return response.data;
  },

  // Find or create car from string (used in Excel import)
  findOrCreateCarFromString: async (data: CarFromStringRequest): Promise<CarFromStringResponse> => {
    const response = await api.post<CarFromStringResponse>('/cars/from-string', data);
    return response.data;
  },
};

export const reportsAPI = {
  // Generate route PDF for a given driver and date (YYYY-MM-DD)
  getDriverRoutePdf: async (
    driverId: string,
    date: string,
    params?: { nome_unidade?: string; nome_marca?: string; status?: string }
  ): Promise<Blob> => {
    const usp = new URLSearchParams({ driver_id: driverId, date });
    if (params?.nome_unidade) usp.append('nome_unidade', params.nome_unidade);
    if (params?.nome_marca) usp.append('nome_marca', params.nome_marca);
    if (params?.status) usp.append('status', params.status);

    const response = await api.get(`/reports/route?${usp.toString()}`, {
      responseType: 'blob'
    });
    return response.data as Blob;
  },
};

export default api;