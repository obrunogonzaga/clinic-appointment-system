import axios from 'axios';
import type { 
  AppointmentListResponse, 
  ExcelUploadResponse, 
  FilterOptions, 
  DashboardStats,
  AppointmentFilter
} from '../types/appointment';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
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
      }
    );
    
    return response.data;
  },

  // Get appointments with filters
  getAppointments: async (filters: AppointmentFilter): Promise<AppointmentListResponse> => {
    const params = new URLSearchParams();
    
    if (filters.nome_unidade) params.append('nome_unidade', filters.nome_unidade);
    if (filters.nome_marca) params.append('nome_marca', filters.nome_marca);
    if (filters.data_inicio) params.append('data_inicio', filters.data_inicio);
    if (filters.data_fim) params.append('data_fim', filters.data_fim);
    if (filters.status) params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    
    const response = await api.get<AppointmentListResponse>(
      `/appointments?${params.toString()}`
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
};

export default api;