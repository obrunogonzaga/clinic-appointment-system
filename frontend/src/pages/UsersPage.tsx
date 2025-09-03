import { useState, useMemo } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import { UserTable } from '../components/users/UserTable';
import { UserFormModal } from '../components/users/UserFormModal';
import { SearchInput } from '../components/ui/SearchInput';
import { Pagination } from '../components/ui/Pagination';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import { ToastContainer } from '../components/ui/Toast';
import type { SortConfig } from '../components/ui/Table';
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from '../hooks/useUsers';
import { useToast } from '../hooks/useToast';
import { useAuth } from '../hooks/useAuth';
import type { User, RegisterData, UserUpdateData } from '../types/auth';

const ITEMS_PER_PAGE = 10;

export function UsersPage() {
  const { user: currentUser } = useAuth();
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: 'created_at',
    direction: 'desc',
  });

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deletingUser, setDeletingUser] = useState<User | null>(null);

  const { toasts, removeToast, success, error } = useToast();

  // Calculate pagination
  const offset = (currentPage - 1) * ITEMS_PER_PAGE;

  // Fetch users
  const { data: usersData, isLoading } = useUsers({
    limit: ITEMS_PER_PAGE,
    offset,
  });

  // Mutations
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();
  const deleteUserMutation = useDeleteUser();

  // Filter and sort users for display
  const processedUsers = useMemo(() => {
    if (!usersData?.users) return [];

    let filtered = usersData.users;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (user) =>
          user.name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortConfig.key as keyof User] as string;
      const bValue = b[sortConfig.key as keyof User] as string;

      if (sortConfig.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [usersData?.users, searchQuery, sortConfig]);

  // Handlers
  const handleSort = (key: string) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page when searching
  };

  const handleCreateUser = async (data: RegisterData) => {
    try {
      await createUserMutation.mutateAsync(data);
      success('Usuário criado com sucesso!');
      setIsCreateModalOpen(false);
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(
        errorMessage || 'Erro ao criar usuário. Tente novamente.'
      );
    }
  };

  const handleUpdateUser = async (data: UserUpdateData) => {
    if (!editingUser) return;

    try {
      await updateUserMutation.mutateAsync({
        userId: editingUser.id,
        data,
      });
      success('Usuário atualizado com sucesso!');
      setEditingUser(null);
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(
        errorMessage || 'Erro ao atualizar usuário. Tente novamente.'
      );
    }
  };

  const handleDeleteUser = async () => {
    if (!deletingUser) return;

    try {
      await deleteUserMutation.mutateAsync(deletingUser.id);
      success('Usuário excluído com sucesso!');
      setDeletingUser(null);
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(
        errorMessage || 'Erro ao excluir usuário. Tente novamente.'
      );
    }
  };

  // Check if current user is admin
  if (!currentUser?.is_admin) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h2 className="text-lg font-medium text-gray-900 mb-2">
            Acesso Negado
          </h2>
          <p className="text-gray-500">
            Você não tem permissão para acessar esta página.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Gerenciamento de Usuários
          </h1>
          <p className="text-gray-600 mt-1">
            Gerencie usuários do sistema
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          Novo Usuário
        </button>
      </div>

      {/* Search */}
      <div className="flex justify-between items-center">
        <SearchInput
          value={searchQuery}
          onChange={handleSearch}
          placeholder="Buscar por nome ou email..."
          className="w-96"
        />
        
        {usersData && (
          <div className="text-sm text-gray-500">
            {usersData.total} usuário{usersData.total !== 1 ? 's' : ''} encontrado{usersData.total !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Users Table */}
      <UserTable
        users={processedUsers}
        loading={isLoading}
        sortConfig={sortConfig}
        onSort={handleSort}
        onEdit={setEditingUser}
        onDelete={setDeletingUser}
      />

      {/* Pagination */}
      {usersData && usersData.total > ITEMS_PER_PAGE && (
        <Pagination
          currentPage={currentPage}
          totalItems={usersData.total}
          itemsPerPage={ITEMS_PER_PAGE}
          onPageChange={handlePageChange}
        />
      )}

      {/* Create User Modal */}
      <UserFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateUser as (data: RegisterData | UserUpdateData) => void}
        mode="create"
        loading={createUserMutation.isPending}
      />

      {/* Edit User Modal */}
      <UserFormModal
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        onSubmit={handleUpdateUser as (data: RegisterData | UserUpdateData) => void}
        user={editingUser || undefined}
        mode="edit"
        loading={updateUserMutation.isPending}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deletingUser}
        onClose={() => setDeletingUser(null)}
        onConfirm={handleDeleteUser}
        title="Excluir Usuário"
        message={`Tem certeza que deseja excluir o usuário "${deletingUser?.name}"? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        type="danger"
        loading={deleteUserMutation.isPending}
      />

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}