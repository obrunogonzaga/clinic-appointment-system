// Removed date-fns dependency - using native Date formatting
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { Table } from '../ui/Table';
import type { Column, SortConfig } from '../ui/Table';
import { Badge } from '../ui/Badge';
import type { User } from '../../types/auth';

interface UserTableProps {
  users: User[];
  loading?: boolean;
  sortConfig?: SortConfig;
  onSort?: (key: string) => void;
  onEdit: (user: User) => void;
  onDelete: (user: User) => void;
}

const ROLE_BADGE: Record<string, { label: string; variant: 'info' | 'success' | 'warning' | 'neutral' }> = {
  admin: { label: 'Administrador', variant: 'info' },
  motorista: { label: 'Motorista', variant: 'success' },
  coletor: { label: 'Coletor', variant: 'warning' },
  colaborador: { label: 'Colaborador', variant: 'neutral' },
};

const STATUS_BADGE: Record<string, { label: string; variant: 'success' | 'error' | 'warning' | 'neutral' }> = {
  aprovado: { label: 'Aprovado', variant: 'success' },
  pendente: { label: 'Pendente', variant: 'warning' },
  rejeitado: { label: 'Rejeitado', variant: 'error' },
  suspenso: { label: 'Suspenso', variant: 'warning' },
  inativo: { label: 'Inativo', variant: 'neutral' },
};

const normalizeRole = (user: User): string => {
  if (user.role && ROLE_BADGE[user.role]) {
    return user.role;
  }
  return user.is_admin ? 'admin' : 'colaborador';
};

const normalizeStatus = (user: User): string => {
  if (user.status && STATUS_BADGE[user.status]) {
    return user.status;
  }
  return user.is_active === false ? 'inativo' : 'aprovado';
};

export function UserTable({
  users,
  loading = false,
  sortConfig,
  onSort,
  onEdit,
  onDelete,
}: UserTableProps) {
  const columns: Column<User>[] = [
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      width: '25%',
    },
    {
      key: 'name',
      label: 'Nome',
      sortable: true,
      width: '25%',
    },
    {
      key: 'role',
      label: 'Perfil',
      width: '15%',
      render: (_, user) => {
        const roleKey = normalizeRole(user);
        const roleInfo = ROLE_BADGE[roleKey] ?? { label: roleKey, variant: 'neutral' };
        return (
          <Badge variant={roleInfo.variant} size="sm">
            {roleInfo.label}
          </Badge>
        );
      },
    },
    {
      key: 'status',
      label: 'Status',
      width: '10%',
      render: (_, user) => {
        const statusKey = normalizeStatus(user);
        const statusInfo = STATUS_BADGE[statusKey] ?? { label: statusKey, variant: 'neutral' };
        return (
          <Badge variant={statusInfo.variant} size="sm">
            {statusInfo.label}
          </Badge>
        );
      },
    },
    {
      key: 'created_at',
      label: 'Criado em',
      sortable: true,
      width: '15%',
      render: (value) => {
        try {
          const date = new Date(value as string);
          return date.toLocaleDateString('pt-BR');
        } catch {
          return '-';
        }
      },
    },
    {
      key: 'actions',
      label: 'Ações',
      width: '10%',
      render: (_, user) => (
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(user)}
            className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-100 rounded"
            title="Editar usuário"
          >
            <PencilIcon className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(user)}
            className="p-1 text-red-600 hover:text-red-800 hover:bg-red-100 rounded"
            title="Excluir usuário"
            disabled={normalizeStatus(user) === 'inativo'}
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <Table
      data={users}
      columns={columns}
      loading={loading}
      sortConfig={sortConfig}
      onSort={onSort}
      emptyMessage="Nenhum usuário encontrado"
      className="shadow-sm"
    />
  );
}
