import { isAxiosError } from 'axios';
import React, { useEffect, useMemo, useState } from 'react';
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import { clientAPI } from '../services/api';
import { ClientFormModal } from '../components/clients/ClientFormModal';
import { ToastContainer } from '../components/ui/Toast';
import { useToast } from '../hooks/useToast';
import type {
  ClientCreateRequest,
  ClientDetail,
  ClientListResponse,
  ClientResponse,
  ClientSummary,
  ClientUpdateRequest,
} from '../types/client';
import { formatCpf } from '../utils/cpf';

const PAGE_SIZE = 20;

const formatDateTime = (value?: string | null): string => {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleString('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
};

export const ClientsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { toasts, success: showSuccess, error: showError, removeToast } = useToast();

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const listQuery = useQuery<ClientListResponse>({
    queryKey: ['clients', { search, page }],
    queryFn: () =>
      clientAPI.listClients({
        search: search.trim() || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
    placeholderData: keepPreviousData,
  });

  const clients: ClientSummary[] = listQuery.data?.clients ?? [];
  const pagination = listQuery.data?.pagination;

  useEffect(() => {
    if (clients.length === 0) {
      return;
    }

    if (!selectedClientId || !clients.some((client) => client.id === selectedClientId)) {
      setSelectedClientId(clients[0].id);
    }
  }, [clients, selectedClientId]);

  const detailQuery = useQuery<ClientResponse>({
    queryKey: ['clients', 'detail', selectedClientId],
    queryFn: () => clientAPI.getClient(selectedClientId!),
    enabled: Boolean(selectedClientId),
  });

  const createClientMutation = useMutation<
    ClientResponse,
    unknown,
    ClientCreateRequest
  >({
    mutationFn: (payload: ClientCreateRequest) => clientAPI.createClient(payload),
    onSuccess: (response) => {
      showSuccess(response.message ?? 'Cliente cadastrado com sucesso.');
      setIsCreateModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      if (response.client?.id) {
        setSelectedClientId(response.client.id);
        queryClient.invalidateQueries({ queryKey: ['clients', 'detail', response.client.id] });
      }
    },
    onError: (error) => {
      if (isAxiosError(error)) {
        const message = error.response?.data?.message ?? 'Não foi possível cadastrar o cliente.';
        showError(message);
      } else {
        showError('Não foi possível cadastrar o cliente.');
      }
    },
  });

  const updateClientMutation = useMutation<
    ClientResponse,
    unknown,
    { id: string; payload: ClientUpdateRequest }
  >({
    mutationFn: ({ id, payload }: { id: string; payload: ClientUpdateRequest }) =>
      clientAPI.updateClient(id, payload),
    onSuccess: (response, variables) => {
      showSuccess(response.message ?? 'Cliente atualizado com sucesso.');
      setIsEditModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['clients', 'detail', variables.id] });
    },
    onError: (error) => {
      if (isAxiosError(error)) {
        const message = error.response?.data?.message ?? 'Não foi possível atualizar o cliente.';
        showError(message);
      } else {
        showError('Não foi possível atualizar o cliente.');
      }
    },
  });

  const selectedClient: ClientDetail | undefined = detailQuery.data?.client;

  const handleCreateSubmit = (payload: ClientCreateRequest | ClientUpdateRequest) => {
    createClientMutation.mutate(payload as ClientCreateRequest);
  };

  const handleUpdateSubmit = (payload: ClientCreateRequest | ClientUpdateRequest) => {
    if (!selectedClientId) {
      return;
    }
    updateClientMutation.mutate({ id: selectedClientId, payload: payload as ClientUpdateRequest });
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
    setPage(1);
  };

  const isListLoading = listQuery.isLoading;
  const isDetailLoading = detailQuery.isLoading;

  const history = useMemo(() => {
    if (!selectedClient) {
      return [];
    }

    return [...selectedClient.appointment_history].sort((a, b) => {
      const dateA = a.data_agendamento ?? a.created_at;
      const dateB = b.data_agendamento ?? b.created_at;
      return dateB.localeCompare(dateA);
    });
  }, [selectedClient]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Clientes</h1>
          <p className="mt-1 text-sm text-gray-600">Gerencie os dados dos pacientes e acompanhe o histórico de agendamentos associados.</p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Novo cliente
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="flex flex-col gap-3 border-b border-gray-200 p-4 md:flex-row md:items-center md:justify-between">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700" htmlFor="client-search">
                  Buscar clientes
                </label>
                <input
                  id="client-search"
                  type="text"
                  value={search}
                  onChange={handleSearchChange}
                  placeholder="Busque por nome, e-mail ou CPF"
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
              <div className="text-sm text-gray-500">
                {pagination ? `Página ${pagination.page} de ${pagination.total_pages}` : '—'}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Cliente
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      CPF
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Último agendamento
                    </th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Total
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isListLoading && (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-500">
                        Carregando clientes...
                      </td>
                    </tr>
                  )}
                  {!isListLoading && clients.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-500">
                        Nenhum cliente encontrado.
                      </td>
                    </tr>
                  )}
                  {!isListLoading &&
                    clients.map((client) => {
                      const isSelected = client.id === selectedClientId;
                      return (
                        <tr
                          key={client.id}
                          className={`cursor-pointer transition hover:bg-blue-50 ${isSelected ? 'bg-blue-50' : ''}`}
                          onClick={() => setSelectedClientId(client.id)}
                        >
                          <td className="px-4 py-3">
                            <div className="text-sm font-medium text-gray-900">{client.nome_completo}</div>
                            {client.email && <div className="text-xs text-gray-500">{client.email}</div>}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-700">{client.cpf_formatado ?? formatCpf(client.cpf)}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{formatDateTime(client.ultima_data_agendamento)}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{client.total_agendamentos}</td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>

            {pagination && (
              <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3 text-sm text-gray-600">
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={!pagination.has_previous}
                  className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Anterior
                </button>
                <span>
                  Mostrando {clients.length} de {pagination.total_items} clientes
                </span>
                <button
                  type="button"
                  onClick={() => setPage((current) => current + 1)}
                  disabled={!pagination.has_next}
                  className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Próxima
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-5">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Detalhes do cliente</h2>
                {selectedClient && (
                  <p className="text-sm text-gray-500">CPF: {formatCpf(selectedClient.cpf)}</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => setIsEditModalOpen(true)}
                disabled={!selectedClient}
                className="inline-flex items-center rounded-md border border-transparent bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Editar
              </button>
            </div>

            <div className="space-y-4 px-4 py-4 text-sm text-gray-700">
              {isDetailLoading && <p>Carregando detalhes...</p>}
              {!isDetailLoading && selectedClient && (
                <>
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Informações de contato</h3>
                    <dl className="mt-1 grid grid-cols-1 gap-2 sm:grid-cols-2">
                      <div>
                        <dt className="text-xs text-gray-500">Telefone</dt>
                        <dd className="text-sm text-gray-900">{selectedClient.telefone ?? '—'}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-500">E-mail</dt>
                        <dd className="text-sm text-gray-900">{selectedClient.email ?? '—'}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Dados de convênio</h3>
                    <dl className="mt-1 grid grid-cols-1 gap-2 sm:grid-cols-2">
                      <div>
                        <dt className="text-xs text-gray-500">Nome do convênio</dt>
                        <dd className="text-sm text-gray-900">{selectedClient.nome_convenio ?? '—'}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-500">Número do convênio</dt>
                        <dd className="text-sm text-gray-900">{selectedClient.numero_convenio ?? '—'}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-500">Carteira</dt>
                        <dd className="text-sm text-gray-900">{selectedClient.carteira_convenio ?? '—'}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Observações</h3>
                    <p className="mt-1 text-sm text-gray-900">{selectedClient.observacoes || 'Nenhuma observação registrada.'}</p>
                  </div>

                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Histórico de agendamentos</h3>
                    {history.length === 0 ? (
                      <p className="mt-1 text-sm text-gray-500">Nenhum agendamento registrado para este cliente.</p>
                    ) : (
                      <ul className="mt-2 space-y-3">
                        {history.map((entry) => (
                          <li key={entry.appointment_id} className="rounded-md border border-gray-200 px-3 py-2">
                            <div className="flex items-center justify-between text-sm text-gray-700">
                              <span className="font-medium text-gray-900">
                                {entry.nome_marca ?? 'Marca não informada'} • {entry.nome_unidade ?? 'Unidade não informada'}
                              </span>
                              <span>{formatDateTime(entry.data_agendamento ?? entry.created_at)}</span>
                            </div>
                            <div className="mt-1 text-xs text-gray-500">
                              {entry.tipo_consulta && <span className="mr-2">{entry.tipo_consulta}</span>}
                              {entry.status && <span className="uppercase tracking-wide">{entry.status}</span>}
                            </div>
                            {entry.observacoes && (
                              <p className="mt-1 text-sm text-gray-700">{entry.observacoes}</p>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <ClientFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        mode="create"
        onSubmit={handleCreateSubmit}
        isSubmitting={createClientMutation.isPending}
      />

      <ClientFormModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        mode="edit"
        initialData={selectedClient}
        onSubmit={handleUpdateSubmit}
        isSubmitting={updateClientMutation.isPending}
      />

      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};
