import { PlusIcon } from '@heroicons/react/24/outline';
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import type { AxiosError } from 'axios';
import React, { useMemo, useState } from 'react';

import { Modal } from '../components/ui/Modal';
import { useToast } from '../hooks/useToast';
import { clientAPI } from '../services/api';
import type { Appointment } from '../types/appointment';
import type {
  Client,
  ClientCreateRequest,
  ClientDetailResponse,
  ClientFilter,
  ClientFormData,
  ClientListResponse,
  ClientResponse,
} from '../types/client';
import { maskCpf } from '../utils/appointmentViewModel';
import { formatDateTime, formatDateTimeLabel } from '../utils/dateUtils';

const sanitizeCpf = (cpf: string): string => cpf.replace(/\D/g, '');

const validateCPF = (cpf: string): boolean => {
  const cleanCPF = sanitizeCpf(cpf);
  if (cleanCPF.length !== 11) {
    return false;
  }

  if (cleanCPF === cleanCPF[0].repeat(11)) {
    return false;
  }

  const digits = cleanCPF.split('').map(Number);

  let sum = 0;
  for (let i = 0; i < 9; i += 1) {
    sum += digits[i] * (10 - i);
  }
  let firstDigit = sum % 11;
  firstDigit = firstDigit < 2 ? 0 : 11 - firstDigit;
  if (digits[9] !== firstDigit) {
    return false;
  }

  sum = 0;
  for (let i = 0; i < 10; i += 1) {
    sum += digits[i] * (11 - i);
  }
  let secondDigit = sum % 11;
  secondDigit = secondDigit < 2 ? 0 : 11 - secondDigit;
  return digits[10] === secondDigit;
};

const validatePhone = (value?: string): boolean => {
  if (!value) {
    return true;
  }

  const digits = value.replace(/\D/g, '');
  return digits.length === 10 || digits.length === 11;
};

const defaultForm: ClientFormData = {
  nome_completo: '',
  cpf: '',
  telefone: '',
  email: '',
  observacoes: '',
  numero_convenio: '',
  nome_convenio: '',
  carteira_convenio: '',
};

export const ClientsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { success: showToastSuccess, error: showToastError } = useToast();

  const [filters, setFilters] = useState<ClientFilter>({
    page: 1,
    page_size: 20,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<ClientFormData>(defaultForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [historyClientId, setHistoryClientId] = useState<string | null>(null);

  const clientsQuery = useQuery<
    ClientListResponse,
    Error,
    ClientListResponse,
    ['clients', ClientFilter]
  >({
    queryKey: ['clients', filters],
    queryFn: () => clientAPI.listClients(filters),
    placeholderData: keepPreviousData,
  });

  const historyQuery = useQuery<
    ClientDetailResponse,
    Error,
    ClientDetailResponse,
    ['clientDetail', string | null]
  >({
    queryKey: ['clientDetail', historyClientId],
    queryFn: () => clientAPI.getClientDetail(historyClientId ?? ''),
    enabled: Boolean(historyClientId),
  });

  type ClientApiError = AxiosError<{ detail?: string }>;

  const createClientMutation = useMutation<
    ClientResponse,
    ClientApiError,
    ClientCreateRequest
  >({
    mutationFn: clientAPI.createClient,
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      showToastSuccess(response.message ?? 'Cliente criado com sucesso');
      setIsFormOpen(false);
      setFormError(null);
      setFormData(defaultForm);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Erro ao criar cliente';
      setFormError(message);
      showToastError(message);
    },
  });

  const updateClientMutation = useMutation<
    ClientResponse,
    ClientApiError,
    { id: string; payload: ClientFormData }
  >({
    mutationFn: ({ id, payload }) =>
      clientAPI.updateClient(id, {
        nome_completo: payload.nome_completo?.trim() || undefined,
        telefone: payload.telefone?.replace(/\D/g, '') || undefined,
        email: payload.email?.trim() || undefined,
        observacoes: payload.observacoes?.trim() || undefined,
        numero_convenio: payload.numero_convenio?.trim() || undefined,
        nome_convenio: payload.nome_convenio?.trim() || undefined,
        carteira_convenio: payload.carteira_convenio?.trim() || undefined,
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['clientDetail', selectedClient?.id] });
      showToastSuccess(response.message ?? 'Cliente atualizado com sucesso');
      setIsFormOpen(false);
      setSelectedClient(null);
      setFormError(null);
    },
    onError: (error) => {
      const message =
        error.response?.data?.detail || 'Erro ao atualizar cliente';
      setFormError(message);
      showToastError(message);
    },
  });

  const isLoading = clientsQuery.isLoading;
  const clientsData = clientsQuery.data;
  const clients = clientsData?.clients ?? [];
  const pagination = clientsData?.pagination;

  const totalPages = pagination?.total_pages ?? 0;
  const currentPage = pagination?.page ?? filters.page ?? 1;

  const isFormSubmitting = createClientMutation.isPending || updateClientMutation.isPending;

  const isEditing = Boolean(selectedClient);

  const handleOpenForm = (client?: Client) => {
    setFormError(null);
    if (client) {
      setSelectedClient(client);
      setFormData({
        nome_completo: client.nome_completo,
        cpf: client.cpf,
        telefone: client.telefone ?? '',
        email: client.email ?? '',
        observacoes: client.observacoes ?? '',
        numero_convenio: client.numero_convenio ?? '',
        nome_convenio: client.nome_convenio ?? '',
        carteira_convenio: client.carteira_convenio ?? '',
      });
    } else {
      setSelectedClient(null);
      setFormData(defaultForm);
    }

    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedClient(null);
    setFormError(null);
    setFormData(defaultForm);
  };

  const handleFormChange = (field: keyof ClientFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmitForm = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);

    const trimmedName = formData.nome_completo.trim();
    if (!trimmedName) {
      setFormError('Nome completo é obrigatório');
      return;
    }

    if (!isEditing) {
      if (!validateCPF(formData.cpf)) {
        setFormError('CPF inválido. Informe 11 dígitos válidos.');
        return;
      }
    }

    if (!validatePhone(formData.telefone)) {
      setFormError('Telefone deve conter 10 ou 11 dígitos.');
      return;
    }

    if (isEditing && selectedClient) {
      updateClientMutation.mutate({ id: selectedClient.id, payload: formData });
      return;
    }

    const payload: ClientCreateRequest = {
      nome_completo: trimmedName,
      cpf: sanitizeCpf(formData.cpf),
      telefone: formData.telefone?.replace(/\D/g, '') || undefined,
      email: formData.email?.trim() || undefined,
      observacoes: formData.observacoes?.trim() || undefined,
      numero_convenio: formData.numero_convenio?.trim() || undefined,
      nome_convenio: formData.nome_convenio?.trim() || undefined,
      carteira_convenio: formData.carteira_convenio?.trim() || undefined,
    };

    createClientMutation.mutate(payload);
  };

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFilters((prev) => ({
      ...prev,
      search: searchTerm.trim() || undefined,
      page: 1,
    }));
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setFilters((prev) => ({
      ...prev,
      search: undefined,
      page: 1,
    }));
  };

  const handleOpenHistory = (clientId: string) => {
    setHistoryClientId(clientId);
  };

  const handleCloseHistory = () => {
    setHistoryClientId(null);
  };

  const handleChangePage = (page: number) => {
    setFilters((prev) => ({
      ...prev,
      page,
    }));
  };

  const historyAppointments: Appointment[] = useMemo(() => {
    if (!historyQuery.data?.history) {
      return [];
    }
    return historyQuery.data.history;
  }, [historyQuery.data]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestão de Clientes</h1>
            <p className="mt-2 text-gray-600">
              Cadastre clientes manualmente ou acompanhe o histórico de agendamentos por CPF.
            </p>
          </div>
          <button
            type="button"
            onClick={() => handleOpenForm()}
            className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <PlusIcon className="mr-2 h-5 w-5" />
            Novo cliente
          </button>
        </div>

        <form onSubmit={handleSearchSubmit} className="mb-6 flex flex-col gap-2 md:flex-row md:items-center">
          <div className="flex grow items-center gap-2">
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Buscar por nome"
            />
            <button
              type="submit"
              className="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Buscar
            </button>
            <button
              type="button"
              onClick={handleClearSearch}
              className="rounded-md border border-transparent px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              Limpar
            </button>
          </div>
        </form>

        <div className="overflow-hidden rounded-lg bg-white shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nome</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">CPF</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Telefone</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Convênio</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Último agendamento</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Agendamentos</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {isLoading && (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-sm text-gray-500">
                      Carregando clientes...
                    </td>
                  </tr>
                )}
                {!isLoading && clients.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-sm text-gray-500">
                      Nenhum cliente encontrado.
                    </td>
                  </tr>
                )}
                {clients.map((client: Client) => (
                  <tr key={client.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4 text-sm font-medium text-gray-900">{client.nome_completo}</td>
                    <td className="px-4 py-4 text-sm text-gray-600">{maskCpf(client.cpf)}</td>
                    <td className="px-4 py-4 text-sm text-gray-600">{client.telefone ? client.telefone : '-'}</td>
                    <td className="px-4 py-4 text-sm text-gray-600">{client.nome_convenio || '-'}</td>
                    <td className="px-4 py-4 text-sm text-gray-600">
                      {client.last_appointment_at
                        ? formatDateTimeLabel(client.last_appointment_at)
                        : '-'}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-600">{client.appointment_count}</td>
                    <td className="px-4 py-4 text-right text-sm">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => handleOpenHistory(client.id)}
                          className="rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-100"
                        >
                          Histórico
                        </button>
                        <button
                          type="button"
                          onClick={() => handleOpenForm(client)}
                          className="rounded-md border border-blue-500 px-3 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50"
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

          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3">
              <div className="text-sm text-gray-600">
                Página {currentPage} de {totalPages}
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={currentPage <= 1}
                  onClick={() => handleChangePage(currentPage - 1)}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Anterior
                </button>
                <button
                  type="button"
                  disabled={currentPage >= totalPages}
                  onClick={() => handleChangePage(currentPage + 1)}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Próxima
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        title={isEditing ? 'Editar cliente' : 'Novo cliente'}
      >
        <form className="space-y-4" onSubmit={handleSubmitForm}>
          {formError && <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</div>}

          <div>
            <label className="block text-sm font-medium text-gray-700">Nome completo *</label>
            <input
              type="text"
              value={formData.nome_completo}
              onChange={(event) => handleFormChange('nome_completo', event.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isFormSubmitting}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">CPF *</label>
            <input
              type="text"
              value={formData.cpf}
              onChange={(event) => handleFormChange('cpf', sanitizeCpf(event.target.value).slice(0, 11))}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isFormSubmitting || isEditing}
              maxLength={11}
              required
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Telefone</label>
              <input
                type="tel"
                value={formData.telefone ?? ''}
                onChange={(event) => handleFormChange('telefone', event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isFormSubmitting}
                placeholder="11999998888"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email ?? ''}
                onChange={(event) => handleFormChange('email', event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isFormSubmitting}
                placeholder="contato@cliente.com"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Número do convênio</label>
              <input
                type="text"
                value={formData.numero_convenio ?? ''}
                onChange={(event) => handleFormChange('numero_convenio', event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isFormSubmitting}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Nome do convênio</label>
              <input
                type="text"
                value={formData.nome_convenio ?? ''}
                onChange={(event) => handleFormChange('nome_convenio', event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isFormSubmitting}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Carteira do convênio</label>
              <input
                type="text"
                value={formData.carteira_convenio ?? ''}
                onChange={(event) => handleFormChange('carteira_convenio', event.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isFormSubmitting}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Observações</label>
            <textarea
              value={formData.observacoes ?? ''}
              onChange={(event) => handleFormChange('observacoes', event.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              rows={3}
              disabled={isFormSubmitting}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleCloseForm}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
              disabled={isFormSubmitting}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              disabled={isFormSubmitting}
            >
              {isEditing ? 'Salvar alterações' : 'Criar cliente'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={Boolean(historyClientId)}
        onClose={handleCloseHistory}
        title="Histórico de agendamentos"
        size="lg"
      >
        {historyQuery.isLoading && (
          <div className="py-6 text-center text-sm text-gray-500">Carregando histórico...</div>
        )}

        {!historyQuery.isLoading && historyAppointments.length === 0 && (
          <div className="py-6 text-center text-sm text-gray-500">
            Nenhum agendamento encontrado para este cliente.
          </div>
        )}

        {!historyQuery.isLoading && historyAppointments.length > 0 && (
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Data</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Unidade</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Marca</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {historyAppointments.map((appointment) => (
                  <tr key={appointment.id}>
                    <td className="px-4 py-2 text-sm text-gray-700">
                      {appointment.data_agendamento
                        ? formatDateTime(
                            appointment.data_agendamento,
                            appointment.hora_agendamento ?? undefined
                          )
                        : formatDateTimeLabel(appointment.created_at)}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-700">{appointment.nome_unidade}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{appointment.nome_marca}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{appointment.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ClientsPage;
