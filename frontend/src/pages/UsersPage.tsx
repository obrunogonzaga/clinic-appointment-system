import { useCallback, useMemo, useState } from 'react';
import {
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  UserGroupIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
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
import { useAdminDashboardStats, usePendingUsers, useApprovePendingUser, useRejectPendingUser } from '../hooks/useAdminApprovals';
import { Modal } from '../components/ui/Modal';
import { authService } from '../services/auth';
import type {
  User,
  RegisterData,
  UserUpdateData,
  UserRole,
  UserStatus,
  UserListParams,
} from '../types/auth';

const ITEMS_PER_PAGE = 10;
const PENDING_PAGE_SIZE = 5;

const STATUS_OPTIONS: Array<{ value: UserStatus | 'all'; label: string }> = [
  { value: 'all', label: 'Todos os status' },
  { value: 'pendente', label: 'Pendente' },
  { value: 'aprovado', label: 'Aprovado' },
  { value: 'rejeitado', label: 'Rejeitado' },
  { value: 'suspenso', label: 'Suspenso' },
  { value: 'inativo', label: 'Inativo' },
];

const ROLE_OPTIONS: Array<{ value: UserRole | 'all'; label: string }> = [
  { value: 'all', label: 'Todos os perfis' },
  { value: 'admin', label: 'Administrador' },
  { value: 'motorista', label: 'Motorista' },
  { value: 'coletor', label: 'Coletor' },
  { value: 'colaborador', label: 'Colaborador' },
];

const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  motorista: 'Motorista',
  coletor: 'Coletor',
  colaborador: 'Colaborador',
};

const STATUS_LABELS: Record<UserStatus, string> = {
  pendente: 'Pendente',
  aprovado: 'Aprovado',
  rejeitado: 'Rejeitado',
  suspenso: 'Suspenso',
  inativo: 'Inativo',
};

const baseNormalizeRole = (user: User): UserRole => {
  if (user.role === 'admin' || user.role === 'motorista' || user.role === 'coletor' || user.role === 'colaborador') {
    return user.role;
  }
  return user.is_admin ? 'admin' : 'colaborador';
};

const baseNormalizeStatus = (user: User): UserStatus => {
  if (user.status === 'pendente' || user.status === 'aprovado' || user.status === 'rejeitado' || user.status === 'suspenso' || user.status === 'inativo') {
    return user.status;
  }
  return user.is_active === false ? 'inativo' : 'aprovado';
};

export function UsersPage() {
  const { user: currentUser } = useAuth();
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: 'created_at',
    direction: 'desc',
  });
  const [statusFilter, setStatusFilter] = useState<UserStatus | 'all'>('all');
  const [roleFilter, setRoleFilter] = useState<UserRole | 'all'>('all');
  const [createdAfter, setCreatedAfter] = useState('');
  const [createdBefore, setCreatedBefore] = useState('');
  const [pendingPage, setPendingPage] = useState(1);
  const [modalType, setModalType] = useState<'approve' | 'reject' | null>(null);
  const [selectedPendingUser, setSelectedPendingUser] = useState<User | null>(null);
  const [approvalMessage, setApprovalMessage] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deletingUser, setDeletingUser] = useState<User | null>(null);

  const { toasts, removeToast, success, error } = useToast();

  const dateFormatter = useMemo(
    () => new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }),
    []
  );

  const formatDateTime = (value?: string | null) => {
    if (!value) return '-';
    try {
      return dateFormatter.format(new Date(value));
    } catch {
      return value;
    }
  };

  const closeActionModal = () => {
    setModalType(null);
    setSelectedPendingUser(null);
    setApprovalMessage('');
    setRejectionReason('');
  };

  const openApproveModal = (targetUser: User) => {
    setSelectedPendingUser(targetUser);
    setApprovalMessage('');
    setModalType('approve');
  };

  const openRejectModal = (targetUser: User) => {
    setSelectedPendingUser(targetUser);
    setRejectionReason('');
    setModalType('reject');
  };

  const offset = (currentPage - 1) * ITEMS_PER_PAGE;

  const usersQueryParams = useMemo<UserListParams>(() => ({
    limit: ITEMS_PER_PAGE,
    offset,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    role: roleFilter !== 'all' ? roleFilter : undefined,
  }), [offset, statusFilter, roleFilter]);

  const { data: usersData, isLoading } = useUsers(usersQueryParams);

  const pendingQueryParams = useMemo(
    () => ({
      limit: PENDING_PAGE_SIZE,
      offset: (pendingPage - 1) * PENDING_PAGE_SIZE,
    }),
    [pendingPage]
  );

  const { data: pendingData, isLoading: isLoadingPending } = usePendingUsers(pendingQueryParams);
  const { data: dashboardStats, isLoading: isLoadingDashboard } = useAdminDashboardStats();

  const approvePendingMutation = useApprovePendingUser();
  const rejectPendingMutation = useRejectPendingUser();

  const pendingUsers = useMemo(() => pendingData?.users ?? [], [pendingData?.users]);
  const pendingApprovals = useMemo(() => dashboardStats?.pending_approvals ?? [], [dashboardStats?.pending_approvals]);
  const recentRegistrations = useMemo(() => dashboardStats?.recent_registrations ?? [], [dashboardStats?.recent_registrations]);

  const statusOverrides = useMemo(() => {
    const map = new Map<string, UserStatus>();
    pendingUsers.forEach((item) => {
      if (item.id) map.set(item.id, 'pendente');
    });
    pendingApprovals.forEach((item) => {
      if (item.id && item.status) map.set(item.id, item.status as UserStatus);
    });
    recentRegistrations.forEach((item) => {
      if (item.id && item.status) map.set(item.id, item.status as UserStatus);
    });
    return map;
  }, [pendingUsers, pendingApprovals, recentRegistrations]);

  const roleOverrides = useMemo(() => {
    const map = new Map<string, UserRole>();
    pendingUsers.forEach((item) => {
      if (item.id && item.role) map.set(item.id, item.role as UserRole);
    });
    pendingApprovals.forEach((item) => {
      if (item.id && item.role) map.set(item.id, item.role as UserRole);
    });
    recentRegistrations.forEach((item) => {
      if (item.id && item.role) map.set(item.id, item.role as UserRole);
    });
    return map;
  }, [pendingUsers, pendingApprovals, recentRegistrations]);

  const normalizeRole = useCallback(
    (user: User): UserRole => {
      const override = user.id ? roleOverrides.get(user.id) : undefined;
      return override ?? baseNormalizeRole(user);
    },
    [roleOverrides]
  );

  const normalizeStatus = useCallback(
    (user: User): UserStatus => {
      const override = user.id ? statusOverrides.get(user.id) : undefined;
      return override ?? baseNormalizeStatus(user);
    },
    [statusOverrides]
  );

  // Mutations
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();
  const deleteUserMutation = useDeleteUser();

  // Filter and sort users for display
  const filterAndSortUsers = useCallback(
    (collection: User[]) => {
      let filtered = [...collection];

      if (statusFilter !== 'all') {
        filtered = filtered.filter((item) => normalizeStatus(item) === statusFilter);
      }

      if (roleFilter !== 'all') {
        filtered = filtered.filter((item) => normalizeRole(item) === roleFilter);
      }

      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(
          (item) =>
            item.name.toLowerCase().includes(query) ||
            item.email.toLowerCase().includes(query)
        );
      }

      if (createdAfter) {
        const minDate = new Date(createdAfter);
        filtered = filtered.filter((item) => {
          if (!item.created_at) return false;
          const createdDate = new Date(item.created_at);
          return !Number.isNaN(createdDate.getTime()) && createdDate >= minDate;
        });
      }

      if (createdBefore) {
        const maxDate = new Date(createdBefore);
        maxDate.setHours(23, 59, 59, 999);
        filtered = filtered.filter((item) => {
          if (!item.created_at) return false;
          const createdDate = new Date(item.created_at);
          return !Number.isNaN(createdDate.getTime()) && createdDate <= maxDate;
        });
      }

      filtered.sort((a, b) => {
        const key = sortConfig.key as keyof User;
        const aValue = a[key];
        const bValue = b[key];

        if (key === 'created_at' && typeof aValue === 'string' && typeof bValue === 'string') {
          const aDate = new Date(aValue).getTime();
          const bDate = new Date(bValue).getTime();
          const compare = (Number.isNaN(aDate) ? 0 : aDate) - (Number.isNaN(bDate) ? 0 : bDate);
          return sortConfig.direction === 'asc' ? compare : -compare;
        }

        const aStr = (aValue ?? '').toString().toLowerCase();
        const bStr = (bValue ?? '').toString().toLowerCase();

        if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });

      return filtered;
    },
    [statusFilter, roleFilter, searchQuery, createdAfter, createdBefore, sortConfig, normalizeStatus, normalizeRole]
  );

  const processedUsers = useMemo(() => {
    if (!usersData?.users) return [];
    const normalized = usersData.users.map((item) => ({
      ...item,
      role: normalizeRole(item),
      status: normalizeStatus(item),
    }));
    return filterAndSortUsers(normalized);
  }, [usersData?.users, filterAndSortUsers, normalizeRole, normalizeStatus]);

  const totalFilteredUsers = processedUsers.length;
  const totalUsersCount = usersData?.total ?? 0;
  const totalPending = pendingData?.total ?? 0;
  const isApproving = approvePendingMutation.isPending;
  const isRejecting = rejectPendingMutation.isPending;
  const roleDistribution = Object.entries(dashboardStats?.users_by_role ?? {});

  const statsCards = [
    {
      label: 'Usuários totais',
      value: dashboardStats?.total_users ?? 0,
      icon: UserGroupIcon,
      iconColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Pendentes',
      value: dashboardStats?.pending_users ?? 0,
      icon: ClockIcon,
      iconColor: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
    {
      label: 'Aprovados',
      value: dashboardStats?.approved_users ?? 0,
      icon: CheckCircleIcon,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Rejeitados',
      value: dashboardStats?.rejected_users ?? 0,
      icon: XCircleIcon,
      iconColor: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      label: 'Suspensos',
      value: dashboardStats?.suspended_users ?? 0,
      icon: ExclamationTriangleIcon,
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

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

  const handlePendingPageChange = (page: number) => {
    setPendingPage(page);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page when searching
  };

  const handleStatusSelect = (value: UserStatus | 'all') => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  const handleRoleSelect = (value: UserRole | 'all') => {
    setRoleFilter(value);
    setCurrentPage(1);
  };

  const handleCreatedAfterChange = (value: string) => {
    setCreatedAfter(value);
    setCurrentPage(1);
  };

  const handleCreatedBeforeChange = (value: string) => {
    setCreatedBefore(value);
    setCurrentPage(1);
  };

  const handleExportCsv = async () => {
    try {
      const response = await authService.listUsers({
        limit: 1000,
        offset: 0,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        role: roleFilter !== 'all' ? roleFilter : undefined,
      });

      const dataset = filterAndSortUsers(
        response.users.map((item) => ({
          ...item,
          role: normalizeRole(item),
          status: normalizeStatus(item),
        }))
      );

      if (dataset.length === 0) {
        error('Nenhum usuário encontrado para exportar com os filtros atuais.');
        return;
      }

      const header = ['Nome', 'Email', 'Perfil', 'Status', 'Criado em'];
      const rows = dataset.map((item) => [
        `"${item.name}"`,
        `"${item.email}"`,
        `"${ROLE_LABELS[normalizeRole(item)]}"`,
        `"${STATUS_LABELS[normalizeStatus(item)]}"`,
        `"${formatDateTime(item.created_at)}"`,
      ]);

      const csvContent = [header.join(';'), ...rows.map((row) => row.join(';'))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `usuarios-${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(url);

      success('Relatório exportado com sucesso!');
    } catch (err) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(message || 'Não foi possível exportar os usuários. Tente novamente.');
    }
  };

  const handleApprovePending = async () => {
    if (!selectedPendingUser) return;

    try {
      await approvePendingMutation.mutateAsync({
        userId: selectedPendingUser.id,
        payload: approvalMessage.trim()
          ? { message: approvalMessage.trim() }
          : undefined,
      });
      success(`Usuário ${selectedPendingUser.name} aprovado com sucesso!`);
      closeActionModal();
    } catch (err) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(message || 'Não foi possível aprovar o usuário. Tente novamente.');
    }
  };

  const handleRejectPending = async () => {
    if (!selectedPendingUser) return;

    if (rejectionReason.trim().length < 10) {
      error('Informe um motivo com pelo menos 10 caracteres.');
      return;
    }

    try {
      await rejectPendingMutation.mutateAsync({
        userId: selectedPendingUser.id,
        payload: { reason: rejectionReason.trim() },
      });
      success(`Usuário ${selectedPendingUser.name} rejeitado.`);
      closeActionModal();
    } catch (err) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      error(message || 'Não foi possível rejeitar o usuário. Tente novamente.');
    }
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
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Gerenciamento de Usuários
          </h1>
          <p className="text-gray-600 mt-1">
            Acompanhe aprovações, estatísticas e mantenha o cadastro em ordem
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={handleExportCsv}
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Exportar CSV
          </button>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Novo Usuário
          </button>
        </div>
      </div>

      {/* Admin Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
        {statsCards.map(({ label, value, icon: Icon, iconColor, bgColor }) => (
          <div
            key={label}
            className="bg-white border border-gray-200 rounded-lg shadow-sm p-5 flex items-center justify-between"
          >
            <div>
              <p className="text-sm text-gray-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-gray-900">
                {isLoadingDashboard ? '...' : value}
              </p>
            </div>
            <div className={`p-3 rounded-full ${bgColor}`}>
              <Icon className={`w-6 h-6 ${iconColor}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Distribuição por Perfil</h2>
            <span className="text-xs text-gray-400">
              {isLoadingDashboard ? 'Atualizando...' : 'Atualizado'}
            </span>
          </div>
          <div className="space-y-3">
            {isLoadingDashboard ? (
              <p className="text-sm text-gray-500">Carregando métricas...</p>
            ) : roleDistribution.length ? (
              roleDistribution.map(([role, count]) => (
                <div key={role} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    {ROLE_LABELS[role as UserRole] ?? role}
                  </span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">
                Nenhum dado disponível para exibir.
              </p>
            )}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Últimos cadastros</h2>
          <div className="space-y-4">
            {isLoadingDashboard ? (
              <p className="text-sm text-gray-500">Carregando cadastros recentes...</p>
            ) : recentRegistrations.length ? (
              recentRegistrations.slice(0, 4).map((item) => (
                <div key={item.id} className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.email}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDateTime(item.created_at)}
                    </p>
                  </div>
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                    {ROLE_LABELS[normalizeRole(item)]}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">Nenhum cadastro recente encontrado.</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between px-6 py-5 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Usuários aguardando aprovação</h2>
            <p className="text-sm text-gray-500">
              Revise e aprove ou rejeite novos cadastros assim que estiverem prontos.
            </p>
          </div>
          <span className="inline-flex items-center justify-center rounded-full px-3 py-1 text-sm font-semibold text-amber-700 bg-amber-100">
            {isLoadingPending ? '...' : totalPending}
          </span>
        </div>
        <div className="divide-y divide-gray-100">
          {isLoadingPending ? (
            <div className="p-6 text-sm text-gray-500">Carregando pendências...</div>
          ) : pendingUsers.length ? (
            pendingUsers.map((pendingUser) => (
              <div
                key={pendingUser.id}
                className="px-6 py-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <p className="font-medium text-gray-900">{pendingUser.name}</p>
                  <p className="text-sm text-gray-500">{pendingUser.email}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium">
                      {ROLE_LABELS[normalizeRole(pendingUser)]}
                    </span>
                    <span>Cadastro em {formatDateTime(pendingUser.created_at)}</span>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => openApproveModal(pendingUser)}
                    disabled={isApproving || isRejecting}
                    className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Aprovar
                  </button>
                  <button
                    onClick={() => openRejectModal(pendingUser)}
                    disabled={isApproving || isRejecting}
                    className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Rejeitar
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-6 text-sm text-gray-500">
              Nenhum usuário pendente no momento.
            </div>
          )}
        </div>
        {totalPending > PENDING_PAGE_SIZE && (
          <div className="px-6 py-4 border-t border-gray-200">
            <Pagination
              currentPage={pendingPage}
              totalItems={totalPending}
              itemsPerPage={PENDING_PAGE_SIZE}
              onPageChange={handlePendingPageChange}
            />
          </div>
        )}
      </div>

      {/* Filters & Search */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 space-y-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <SearchInput
            value={searchQuery}
            onChange={handleSearch}
            placeholder="Buscar por nome ou email..."
            className="w-full lg:max-w-md"
          />
          <div className="text-sm text-gray-500">
            {totalFilteredUsers} de {totalUsersCount} usuário{totalUsersCount !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(event) => handleStatusSelect(event.target.value as UserStatus | 'all')}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Perfil</label>
            <select
              value={roleFilter}
              onChange={(event) => handleRoleSelect(event.target.value as UserRole | 'all')}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              {ROLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Criado a partir de</label>
            <input
              type="date"
              value={createdAfter}
              onChange={(event) => handleCreatedAfterChange(event.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Criado até</label>
            <input
              type="date"
              value={createdBefore}
              onChange={(event) => handleCreatedBeforeChange(event.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            />
          </div>
        </div>
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

      {/* Approval Modal */}
      <Modal
        isOpen={modalType === 'approve'}
        onClose={closeActionModal}
        title={`Aprovar ${selectedPendingUser?.name || 'usuário'}`}
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Confirme a aprovação do usuário. Opcionalmente, adicione uma mensagem que será enviada por email.
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mensagem (opcional)
            </label>
            <textarea
              value={approvalMessage}
              onChange={(event) => setApprovalMessage(event.target.value)}
              rows={3}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Bem-vindo ao sistema! Seu acesso foi liberado."
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={closeActionModal}
              disabled={isApproving}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleApprovePending}
              disabled={isApproving}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isApproving ? (
                <span className="flex items-center">
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Processando...
                </span>
              ) : (
                'Aprovar'
              )}
            </button>
          </div>
        </div>
      </Modal>

      {/* Rejection Modal */}
      <Modal
        isOpen={modalType === 'reject'}
        onClose={closeActionModal}
        title={`Rejeitar ${selectedPendingUser?.name || 'usuário'}`}
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Informe o motivo da rejeição. Esse texto será enviado ao usuário por email.
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motivo (mínimo 10 caracteres)
            </label>
            <textarea
              value={rejectionReason}
              onChange={(event) => setRejectionReason(event.target.value)}
              rows={4}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-red-500 focus:ring-red-500"
              placeholder="Explique por que o cadastro foi rejeitado."
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={closeActionModal}
              disabled={isRejecting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleRejectPending}
              disabled={isRejecting}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRejecting ? (
                <span className="flex items-center">
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Processando...
                </span>
              ) : (
                'Rejeitar'
              )}
            </button>
          </div>
        </div>
      </Modal>

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
