import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '../services/auth';
import type {
  AdminDashboardStats,
  PendingUsersResponse,
  UserApprovalPayload,
  UserRejectionPayload,
} from '../types/auth';
import { userKeys } from './useUsers';

export const adminKeys = {
  all: ['admin'] as const,
  dashboard: () => [...adminKeys.all, 'dashboard'] as const,
  pending: (params: { limit?: number; offset?: number }) => [
    ...adminKeys.all,
    'pending',
    params,
  ] as const,
};

export function useAdminDashboardStats() {
  return useQuery<AdminDashboardStats>({
    queryKey: adminKeys.dashboard(),
    queryFn: () => authService.getAdminDashboardStats(),
    staleTime: 2 * 60 * 1000,
  });
}

export function usePendingUsers(params: { limit?: number; offset?: number } = {}) {
  return useQuery<PendingUsersResponse>({
    queryKey: adminKeys.pending(params),
    queryFn: () => authService.getPendingUsers(params),
    staleTime: 30 * 1000,
  });
}

export function useApprovePendingUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload?: UserApprovalPayload }) =>
      authService.approvePendingUser(userId, payload ?? {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.dashboard() });
      queryClient.invalidateQueries({ queryKey: adminKeys.all });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}

export function useRejectPendingUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: UserRejectionPayload }) =>
      authService.rejectPendingUser(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.dashboard() });
      queryClient.invalidateQueries({ queryKey: adminKeys.all });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}
