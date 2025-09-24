import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import React from 'react';
import { useForm } from 'react-hook-form';
import { logisticsPackageAPI, driverAPI, collectorAPI, carAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { ToastContainer } from '../components/ui/Toast';
import type { LogisticsPackageCreateRequest } from '../types/logistics-package';

type CreateFormValues = {
  nome: string;
  descricao: string;
  driver_id: string;
  collector_id: string;
  car_id: string;
};

export const LogisticsPackagesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { success: showToastSuccess, error: showToastError, toasts, removeToast } = useToast();

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<CreateFormValues>({
    defaultValues: {
      nome: '',
      descricao: '',
      driver_id: '',
      collector_id: '',
      car_id: '',
    },
  });

  const { data: packagesData, isLoading: isLoadingPackages } = useQuery({
    queryKey: ['logisticsPackages'],
    queryFn: () => logisticsPackageAPI.listPackages(),
    refetchOnWindowFocus: false,
  });

  const { data: driversData } = useQuery({
    queryKey: ['activeDrivers'],
    queryFn: () => driverAPI.getActiveDrivers(),
    refetchOnWindowFocus: false,
  });

  const { data: collectorsData } = useQuery({
    queryKey: ['activeCollectors'],
    queryFn: () => collectorAPI.getActiveCollectors(),
    refetchOnWindowFocus: false,
  });

  const { data: carsData } = useQuery({
    queryKey: ['activeCars'],
    queryFn: () => carAPI.getActiveCars(),
    refetchOnWindowFocus: false,
  });

  const packages = packagesData?.data ?? [];
  const drivers = driversData?.drivers ?? [];
  const collectors = collectorsData?.collectors ?? [];
  const cars = carsData?.cars ?? [];

  const invalidatePackages = () => {
    queryClient.invalidateQueries({ queryKey: ['logisticsPackages'] });
    queryClient.invalidateQueries({ queryKey: ['activeLogisticsPackages'] });
  };

  const createMutation = useMutation({
    mutationFn: (payload: LogisticsPackageCreateRequest) => logisticsPackageAPI.createPackage(payload),
    onSuccess: (response) => {
      showToastSuccess(response.message ?? 'Pacote criado com sucesso.');
      invalidatePackages();
      reset({ nome: '', descricao: '', driver_id: '', collector_id: '', car_id: '' });
    },
    onError: (error) => {
      const fallback = 'Não foi possível criar o pacote logístico.';
      if (isAxiosError(error)) {
        const message = error.response?.data?.detail ?? error.message ?? fallback;
        showToastError(message);
      } else {
        showToastError(fallback);
      }
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'Ativo' | 'Inativo' }) =>
      logisticsPackageAPI.updatePackage(id, { status }),
    onSuccess: (response) => {
      showToastSuccess(response.message ?? 'Pacote atualizado.');
      invalidatePackages();
    },
    onError: () => {
      showToastError('Não foi possível atualizar o status do pacote.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => logisticsPackageAPI.deletePackage(id),
    onSuccess: (response) => {
      showToastSuccess(response.message);
      invalidatePackages();
    },
    onError: () => {
      showToastError('Não foi possível remover o pacote.');
    },
  });

  const onSubmit = handleSubmit(async (values) => {
    await createMutation.mutateAsync({
      nome: values.nome.trim(),
      descricao: values.descricao.trim() || undefined,
      driver_id: values.driver_id,
      collector_id: values.collector_id,
      car_id: values.car_id,
    });
  });

  const handleStatusToggle = (id: string, currentStatus: 'Ativo' | 'Inativo') => {
    const nextStatus = currentStatus === 'Ativo' ? 'Inativo' : 'Ativo';
    updateStatusMutation.mutate({ id, status: nextStatus });
  };

  const handleDelete = (id: string) => {
    if (!window.confirm('Deseja realmente remover este pacote logístico?')) {
      return;
    }
    deleteMutation.mutate(id);
  };

  return (
    <div className="space-y-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-gray-900">Pacotes logísticos</h1>
        <p className="mt-1 text-sm text-gray-500">
          Cadastre combinações reutilizáveis de motorista, coletora e carro para agilizar os agendamentos.
        </p>

        <form className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2" onSubmit={onSubmit}>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Nome do pacote *</label>
            <input
              type="text"
              {...register('nome', { required: true })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Ex.: Manhã Centro"
              disabled={isSubmitting || createMutation.isPending}
            />
            {errors.nome && (
              <p className="mt-1 text-sm text-red-600">Informe o nome do pacote.</p>
            )}
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Descrição</label>
            <textarea
              rows={2}
              {...register('descricao')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Observações adicionais sobre o uso deste pacote"
              disabled={isSubmitting || createMutation.isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Motorista *</label>
            <select
              {...register('driver_id', { required: true })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting || createMutation.isPending}
            >
              <option value="">Selecione um motorista</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.nome_completo}
                </option>
              ))}
            </select>
            {errors.driver_id && (
              <p className="mt-1 text-sm text-red-600">Escolha um motorista ativo.</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Coletora *</label>
            <select
              {...register('collector_id', { required: true })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting || createMutation.isPending}
            >
              <option value="">Selecione uma coletora</option>
              {collectors.map((collector) => (
                <option key={collector.id} value={collector.id}>
                  {collector.nome_completo}
                </option>
              ))}
            </select>
            {errors.collector_id && (
              <p className="mt-1 text-sm text-red-600">Escolha uma coletora ativa.</p>
            )}
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Carro *</label>
            <select
              {...register('car_id', { required: true })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting || createMutation.isPending}
            >
              <option value="">Selecione um carro</option>
              {cars.map((car) => (
                <option key={car.id} value={car.id}>
                  {car.nome}{car.unidade ? ` • ${car.unidade}` : ''}
                </option>
              ))}
            </select>
            {errors.car_id && (
              <p className="mt-1 text-sm text-red-600">Escolha um carro disponível.</p>
            )}
          </div>

          <div className="md:col-span-2 flex justify-end">
            <button
              type="submit"
              className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60"
              disabled={isSubmitting || createMutation.isPending}
            >
              {createMutation.isPending ? 'Salvando...' : 'Criar pacote'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Pacotes cadastrados</h2>
          <span className="text-sm text-gray-500">
            {packages.length} pacote{packages.length === 1 ? '' : 's'} encontrado{packages.length === 1 ? '' : 's'}
          </span>
        </div>

        {isLoadingPackages ? (
          <p className="mt-6 text-sm text-gray-500">Carregando pacotes...</p>
        ) : packages.length === 0 ? (
          <p className="mt-6 text-sm text-gray-500">Nenhum pacote cadastrado até o momento.</p>
        ) : (
          <div className="mt-6 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Pacote</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Motorista</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Coletora</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Carro</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Status</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {packages.map((pkg) => (
                  <tr key={pkg.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{pkg.nome}</div>
                      {pkg.descricao && (
                        <div className="text-xs text-gray-500">{pkg.descricao}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-700">{pkg.driver_nome}</td>
                    <td className="px-4 py-3 text-gray-700">{pkg.collector_nome}</td>
                    <td className="px-4 py-3 text-gray-700">{pkg.car_display_name}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${
                        pkg.status === 'Ativo'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {pkg.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleStatusToggle(pkg.id, pkg.status)}
                          className="rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-100"
                          disabled={updateStatusMutation.isPending}
                        >
                          {pkg.status === 'Ativo' ? 'Inativar' : 'Ativar'}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(pkg.id)}
                          className="rounded-md border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                          disabled={deleteMutation.isPending}
                        >
                          Remover
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};

export default LogisticsPackagesPage;
