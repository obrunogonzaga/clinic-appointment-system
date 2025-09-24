import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { appointmentAPI } from '../services/api';
import type {
  Appointment,
  AppointmentUpdateRequest,
} from '../types/appointment';

export const appointmentQueryKeys = {
  all: ['appointments'] as const,
  detail: (appointmentId: string) =>
    [...appointmentQueryKeys.all, 'detail', appointmentId] as const,
};

export function useAppointmentDetails(appointmentId: string | null) {
  return useQuery<Appointment, Error>({
    queryKey: appointmentId
      ? appointmentQueryKeys.detail(appointmentId)
      : [...appointmentQueryKeys.all, 'detail', 'unknown'],
    queryFn: () => {
      if (!appointmentId) {
        throw new Error('ID do agendamento não informado.');
      }
      return appointmentAPI.getAppointmentById(appointmentId);
    },
    enabled: Boolean(appointmentId),
    staleTime: 2 * 60 * 1000,
  });
}

type UpdateVariables = {
  appointmentId: string;
  data: AppointmentUpdateRequest;
};

export function sanitizeUpdatePayload(
  payload: AppointmentUpdateRequest
): AppointmentUpdateRequest {
  return Object.fromEntries(
    Object.entries(payload).filter(([, value]) => value !== undefined)
  ) as AppointmentUpdateRequest;
}

export function useUpdateAppointment() {
  const queryClient = useQueryClient();

  return useMutation<Appointment, Error, UpdateVariables>({
    mutationFn: ({ appointmentId, data }) =>
      appointmentAPI.updateAppointment(
        appointmentId,
        sanitizeUpdatePayload(data)
      ),
    onSuccess: (updatedAppointment) => {
      queryClient.setQueryData<Appointment>(
        appointmentQueryKeys.detail(updatedAppointment.id),
        updatedAppointment
      );
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    },
  });
}
