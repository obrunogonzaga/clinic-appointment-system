import type { Client } from '../types/client';
import { maskCpf } from '../utils/appointmentViewModel';

interface ClientTableProps {
  clients: Client[];
  onEdit: (client: Client) => void;
  onViewHistory: (client: Client) => void;
  isLoading?: boolean;
}

export function ClientTable({ clients, onEdit, onViewHistory, isLoading = false }: ClientTableProps) {
  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Carregando clientes...</p>
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center rounded-lg border border-dashed border-gray-200">
        <p className="text-sm text-gray-500">Nenhum cliente encontrado.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Nome
            </th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              CPF
            </th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Telefone
            </th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Último agendamento
            </th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Ações
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {clients.map((client) => (
            <tr key={client.id} className="hover:bg-gray-50">
              <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">{client.nome}</td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{maskCpf(client.cpf)}</td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                {client.telefone ? client.telefone : '—'}
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">
                {client.ultimo_agendamento_em
                  ? new Date(client.ultimo_agendamento_em).toLocaleDateString('pt-BR')
                  : '—'}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onViewHistory(client)}
                    className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Histórico
                  </button>
                  <button
                    type="button"
                    onClick={() => onEdit(client)}
                    className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Editar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
