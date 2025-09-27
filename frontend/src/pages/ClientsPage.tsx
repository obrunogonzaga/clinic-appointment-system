import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { ClientFormModal, type ClientFormValues } from '../components/ClientFormModal';
import { ClientHistoryModal } from '../components/ClientHistoryModal';
import { ClientTable } from '../components/ClientTable';
import { clientAPI } from '../services/api';
import type {
  Client,
  ClientCreateRequest,
  ClientDataResponse,
  ClientDetail,
  ClientDetailResponse,
  ClientUpdateRequest,
} from '../types/client';

const CLIENTS_PAGE_SIZE = 10;

export function ClientsPage() {
  const queryClient = useQueryClient();
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | undefined>();
  const [formError, setFormError] = useState<string | null>(null);
  const [historyClient, setHistoryClient] = useState<ClientDetail | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const {
    data: clientsData,
    isLoading: isLoadingClients,
    isError: isClientsError,
  } = useQuery({
    queryKey: ['clients', { searchTerm, page }],
    queryFn: () =>
      clientAPI.getClients({
        search: searchTerm || undefined,
        page,
        page_size: CLIENTS_PAGE_SIZE,
      }),
    keepPreviousData: true,
  });

  const createClientMutation = useMutation<ClientDataResponse, unknown, ClientCreateRequest>({
    mutationFn: clientAPI.createClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setIsFormOpen(false);
      setSelectedClient(undefined);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Erro ao cadastrar cliente';
      setFormError(message);
    },
  });

  const updateClientMutation = useMutation<
    ClientDataResponse,
    unknown,
    { id: string; data: ClientUpdateRequest }
  >({
    mutationFn: ({ id, data }) => clientAPI.updateClient(id, data),
    onSuccess: (response, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      if (isHistoryOpen && historyClient && historyClient.id === variables.id) {
        setHistoryClient(response.data);
      }
      setIsFormOpen(false);
      setSelectedClient(undefined);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Erro ao atualizar cliente';
      setFormError(message);
    },
  });

  const historyMutation = useMutation<ClientDetailResponse, unknown, string>({
    mutationFn: (id) => clientAPI.getClientDetail(id),
    onSuccess: (response) => {
      setHistoryClient(response.client);
      setHistoryError(null);
      setIsHistoryOpen(true);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Não foi possível carregar o histórico do cliente';
      setHistoryError(message);
    },
  });

  const clients = clientsData?.clients ?? [];
  const pagination = clientsData?.pagination;

  const handleSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setSearchTerm(searchInput.trim());
    setPage(1);
  };

  const handleResetSearch = () => {
    setSearchInput('');
    setSearchTerm('');
    setPage(1);
  };

  const handleNewClient = () => {
    setSelectedClient(undefined);
    setFormError(null);
    setIsFormOpen(true);
  };

  const handleEditClient = (client: Client) => {
    setSelectedClient(client);
    setFormError(null);
    setIsFormOpen(true);
  };

  const sanitizeFormValues = (values: ClientFormValues): ClientFormValues => ({
    nome: values.nome.trim(),
    cpf: values.cpf.replace(/\D/g, ''),
    telefone: values.telefone ? values.telefone.replace(/\D/g, '') : '',
    email: values.email ? values.email.trim() : '',
    observacoes: values.observacoes ? values.observacoes.trim() : '',
  });

  const handleFormSubmit = (values: ClientFormValues) => {
    const sanitized = sanitizeFormValues(values);

    if (selectedClient) {
      const updatePayload: ClientUpdateRequest = {
        nome: sanitized.nome,
        telefone: sanitized.telefone || undefined,
        email: sanitized.email || undefined,
        observacoes: sanitized.observacoes || undefined,
      };
      updateClientMutation.mutate({ id: selectedClient.id, data: updatePayload });
      return;
    }

    createClientMutation.mutate({
      nome: sanitized.nome,
      cpf: sanitized.cpf,
      telefone: sanitized.telefone || undefined,
      email: sanitized.email || undefined,
      observacoes: sanitized.observacoes || undefined,
    });
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedClient(undefined);
    setFormError(null);
  };

  const handleViewHistory = (client: Client) => {
    setHistoryError(null);
    historyMutation.mutate(client.id);
  };

  const handleCloseHistory = () => {
    setIsHistoryOpen(false);
    setHistoryClient(null);
  };

  const isSubmitting = createClientMutation.isPending || updateClientMutation.isPending;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestão de Clientes</h1>
            <p className="text-gray-600">Acompanhe os pacientes cadastrados e seus agendamentos.</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleNewClient}
              className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Novo cliente
            </button>
          </div>
        </div>

        <form className="mb-6" onSubmit={handleSearchSubmit}>
          <div className="flex flex-col gap-3 rounded-lg bg-white p-4 shadow-sm md:flex-row md:items-center">
            <div className="flex-1">
              <label htmlFor="client-search" className="block text-sm font-medium text-gray-700">
                Buscar por nome ou CPF
              </label>
              <input
                id="client-search"
                type="text"
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Ex.: Maria Silva ou 12345678901"
              />
            </div>
            <div className="flex items-center gap-3">
              <button
                type="submit"
                className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Buscar
              </button>
              <button
                type="button"
                onClick={handleResetSearch}
                className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Limpar
              </button>
            </div>
          </div>
        </form>

        {historyError ? (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {historyError}
          </div>
        ) : null}

        {isClientsError ? (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Não foi possível carregar a lista de clientes. Tente novamente em instantes.
          </div>
        ) : (
          <ClientTable
            clients={clients}
            onEdit={handleEditClient}
            onViewHistory={handleViewHistory}
            isLoading={isLoadingClients}
          />
        )}

        {pagination && (pagination.total_pages > 1 || pagination.has_previous || pagination.has_next) ? (
          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Página {pagination.page} de {pagination.total_pages}
            </p>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setPage((current) => Math.max(1, current - 1))}
                disabled={!pagination.has_previous}
                className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                type="button"
                onClick={() => setPage((current) => current + 1)}
                disabled={!pagination.has_next}
                className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Próxima
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <ClientFormModal
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
        client={selectedClient}
        serverError={formError}
      />

      <ClientHistoryModal
        isOpen={isHistoryOpen}
        onClose={handleCloseHistory}
        client={historyClient}
      />
    </div>
  );
}
