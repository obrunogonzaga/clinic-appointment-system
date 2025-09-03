// Removed date-fns dependency - using native Date formatting
import { PencilIcon, TrashIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
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
      key: 'is_admin',
      label: 'Tipo',
      width: '15%',
      render: (value) => (
        <div className="flex items-center">
          {(value as boolean) ? (
            <>
              <ShieldCheckIcon className="w-4 h-4 text-green-500 mr-1" />
              <Badge variant="info" size="sm">
                Admin
              </Badge>
            </>
          ) : (
            <Badge variant="neutral" size="sm">
              Usuário
            </Badge>
          )}
        </div>
      ),
    },
    {
      key: 'is_active',
      label: 'Status',
      width: '10%',
      render: (value) => (
        <Badge variant={(value as boolean) ? 'success' : 'error'} size="sm">
          {(value as boolean) ? 'Ativo' : 'Inativo'}
        </Badge>
      ),
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
            disabled={!user.is_active}
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