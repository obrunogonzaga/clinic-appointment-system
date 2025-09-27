import { Modal } from './ui/Modal';
import type { ClientDetail, ClientHistoryEntry } from '../types/client';

interface ClientHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  client: ClientDetail | null;
}

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleDateString('pt-BR');
  } catch {
    return value;
  }
};

const formatTime = (value?: string | null) => (value ? value : '—');

const sortHistory = (history: ClientHistoryEntry[]) =>
  [...history].sort((a, b) => {
    const dateA = a.data_agendamento ? new Date(a.data_agendamento).getTime() : 0;
    const dateB = b.data_agendamento ? new Date(b.data_agendamento).getTime() : 0;
    return dateB - dateA;
  });

export function ClientHistoryModal({ isOpen, onClose, client }: ClientHistoryModalProps) {
  if (!client) {
    return null;
  }

  const history = sortHistory(client.historico_agendamentos);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Histórico de ${client.nome}`} size="lg">
      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div>
            <p className="text-sm text-gray-500">CPF</p>
            <p className="text-base font-medium text-gray-900">{client.cpf}</p>
          </div>
          {client.telefone ? (
            <div>
              <p className="text-sm text-gray-500">Telefone</p>
              <p className="text-base font-medium text-gray-900">{client.telefone}</p>
            </div>
          ) : null}
          {client.email ? (
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-base font-medium text-gray-900">{client.email}</p>
            </div>
          ) : null}
          {client.total_agendamentos > 0 ? (
            <div>
              <p className="text-sm text-gray-500">Total de agendamentos</p>
              <p className="text-base font-medium text-gray-900">{client.total_agendamentos}</p>
            </div>
          ) : null}
        </div>

        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Data
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Hora
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Unidade
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Marca
                </th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-500">
                    Nenhum agendamento registrado para este cliente.
                  </td>
                </tr>
              ) : (
                history.map((entry) => (
                  <tr key={entry.appointment_id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{formatDate(entry.data_agendamento)}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{formatTime(entry.hora_agendamento)}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{entry.nome_unidade ?? '—'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{entry.nome_marca ?? '—'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{entry.status ?? '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Modal>
  );
}
