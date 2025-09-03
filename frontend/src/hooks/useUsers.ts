import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '../services/auth';
import type {
  UserListParams,
  UserListResponse,
  UserUpdateData,
  User,
  RegisterData,
} from '../types/auth';

// Query keys
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (params: UserListParams) => [...userKeys.lists(), params] as const,
  detail: (id: string) => [...userKeys.all, 'detail', id] as const,
};

// Hook to list users with pagination
export function useUsers(params: UserListParams = {}) {
  return useQuery({
    queryKey: userKeys.list(params),
    queryFn: () => authService.listUsers(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook to create a new user
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: RegisterData) => authService.createUser(userData),
    onSuccess: () => {
      // Invalidate and refetch user lists
      queryClient.invalidateQueries({
        queryKey: userKeys.lists(),
      });
    },
  });
}

// Hook to update a user
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UserUpdateData }) =>
      authService.updateUser(userId, data),
    onSuccess: (updatedUser, { userId }) => {
      // Update the user in the cache
      queryClient.setQueryData<User>(userKeys.detail(userId), updatedUser);
      
      // Update user lists
      queryClient.setQueriesData<UserListResponse>(
        { queryKey: userKeys.lists() },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            users: old.users.map((user) =>
              user.id === userId ? updatedUser : user
            ),
          };
        }
      );

      // Invalidate and refetch user lists to ensure consistency
      queryClient.invalidateQueries({
        queryKey: userKeys.lists(),
      });
    },
  });
}

// Hook to delete a user
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => authService.deleteUser(userId),
    onSuccess: (_, userId) => {
      // Remove user from lists or mark as inactive
      queryClient.setQueriesData<UserListResponse>(
        { queryKey: userKeys.lists() },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            users: old.users.map((user) =>
              user.id === userId ? { ...user, is_active: false } : user
            ),
          };
        }
      );

      // Invalidate and refetch user lists
      queryClient.invalidateQueries({
        queryKey: userKeys.lists(),
      });
    },
  });
}

// Hook for optimistic updates with error handling
export function useOptimisticUserUpdate() {
  const queryClient = useQueryClient();

  return {
    optimisticUpdate: (userId: string, updates: Partial<User>) => {
      // Cancel any outgoing refetches
      queryClient.cancelQueries({ queryKey: userKeys.lists() });

      // Snapshot the previous value
      const previousData = queryClient.getQueriesData<UserListResponse>({
        queryKey: userKeys.lists(),
      });

      // Optimistically update to the new value
      queryClient.setQueriesData<UserListResponse>(
        { queryKey: userKeys.lists() },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            users: old.users.map((user) =>
              user.id === userId ? { ...user, ...updates } : user
            ),
          };
        }
      );

      // Return a context object with the snapshotted value
      return { previousData };
    },

    rollback: (context: { previousData: Array<[unknown[], unknown]> }) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      context.previousData.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey as unknown[], data);
      });
    },
  };
}