import { useEffect, useMemo } from 'react';
import { Controller, useForm, useWatch, type SubmitHandler, type Resolver } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { Modal } from './ui/Modal';
import type { AppointmentCreateRequest } from '../types/appointment';
import type { ActiveDriver } from '../types/driver';
import type { ActiveCollector } from '../types/collector';
import { APPOINTMENT_STATUS_OPTIONS } from '../utils/appointmentViewModel';
import type { Tag } from '../types/tag';
import type { LogisticsPackage } from '../types/logistics-package';
import { TagSelector } from './tags/TagSelector';

interface AppointmentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AppointmentCreateRequest) => Promise<void> | void;
  isSubmitting?: boolean;
  brands: string[];
  units: string[];
  statuses?: string[];
  drivers: ActiveDriver[];
  collectors: ActiveCollector[];
  tags: Tag[];
  maxTags?: number;
  logisticsPackages: LogisticsPackage[];
}

const DEFAULT_BRAND = 'Sergio Franco';
const DEFAULT_UNIT = 'LM-RECREIO 2 PEDRA DE ITAUNA D';
const DEFAULT_STATUS = 'Pendente';
const TIME_REGEX = /^([01]\d|2[0-3]):[0-5]\d$/;

const formSchema = z.object({
  nome_marca: z.string().trim().min(1, 'Informe a marca/clinica'),
  nome_unidade: z.string().trim().min(1, 'Informe a unidade'),
  nome_paciente: z.string().trim().min(1, 'Informe o nome do paciente'),
  date: z.string().trim().optional(),
  time: z
    .string()
    .trim()
    .optional()
    .refine((value) => {
      if (!value) {
        return true;
      }

      return TIME_REGEX.test(value);
    }, 'Hora inválida (use HH:MM)'),
  tipo_consulta: z.string().trim().default(''),
  cip: z.string().trim().max(60, 'CIP deve ter no máximo 60 caracteres').default(''),
  status: z.string().trim().min(1, 'Selecione o status'),
  telefone: z
    .string()
    .trim()
    .min(1, 'Informe o telefone do paciente')
    .refine((value) => {
      const digits = value.replace(/\D/g, '');
      return digits.length === 10 || digits.length === 11;
    }, 'Telefone deve conter 10 ou 11 dígitos'),
  carro: z.string().trim().default(''),
  logistics_package_id: z.string().trim().default(''),
  observacoes: z.string().trim().default(''),
  driver_id: z.string().trim().default(''),
  collector_id: z.string().trim().default(''),
  numero_convenio: z.string().trim().default(''),
  nome_convenio: z.string().trim().default(''),
  carteira_convenio: z.string().trim().default(''),
  tags: z.array(z.string()).default([]),
});

type FormValues = z.infer<typeof formSchema>;

export function AppointmentFormModal({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  brands,
  units,
  statuses,
  drivers,
  collectors,
  tags,
  maxTags = 5,
  logisticsPackages,
}: AppointmentFormModalProps) {
  const statusChoices = useMemo(() => {
    const provided = statuses && statuses.length > 0 ? statuses : [...APPOINTMENT_STATUS_OPTIONS];
    if (provided.includes(DEFAULT_STATUS)) {
      return provided;
    }

    return [DEFAULT_STATUS, ...provided];
  }, [statuses]);

  const defaultStatus = useMemo(() => {
    if (statusChoices.includes(DEFAULT_STATUS)) {
      return DEFAULT_STATUS;
    }

    return statusChoices[0] ?? DEFAULT_STATUS;
  }, [statusChoices]);

  const brandOptions = useMemo(() => {
    void brands;
    return [DEFAULT_BRAND];
  }, [brands]);

  const unitOptions = useMemo(() => {
    void units;
    return [DEFAULT_UNIT];
  }, [units]);

  const defaultValues = useMemo<FormValues>(
    () => ({
      nome_marca: DEFAULT_BRAND,
      nome_unidade: DEFAULT_UNIT,
      nome_paciente: '',
      date: '',
      time: '',
      tipo_consulta: '',
      cip: '',
      status: defaultStatus,
      telefone: '',
      carro: '',
      logistics_package_id: '',
      observacoes: '',
      driver_id: '',
      collector_id: '',
      numero_convenio: '',
      nome_convenio: '',
      carteira_convenio: '',
      tags: [],
    }),
    [defaultStatus]
  );

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema) as unknown as Resolver<FormValues>,
    defaultValues: defaultValues as FormValues,
  });

  const logisticsPackagesById = useMemo(() => {
    return new Map(logisticsPackages.map(pkg => [pkg.id, pkg]));
  }, [logisticsPackages]);

  const selectedLogisticsPackageId = useWatch({
    control,
    name: 'logistics_package_id',
  });

  useEffect(() => {
    if (isOpen) {
      reset(defaultValues);
    }
  }, [isOpen, reset, defaultValues]);

  useEffect(() => {
    if (!selectedLogisticsPackageId) {
      return;
    }

    const selectedPackage = logisticsPackagesById.get(selectedLogisticsPackageId);
    if (!selectedPackage) {
      return;
    }

    setValue('driver_id', selectedPackage.driver_id, { shouldDirty: true });
    setValue('collector_id', selectedPackage.collector_id, { shouldDirty: true });
    setValue('carro', selectedPackage.car_display_name, { shouldDirty: true });
  }, [selectedLogisticsPackageId, logisticsPackagesById, setValue]);

  const handleClose = () => {
    reset(defaultValues);
    onClose();
  };

  const onSubmitForm: SubmitHandler<FormValues> = (values) => {
    const trimmedDate = values.date?.trim();
    const trimmedTime = values.time?.trim();

    let scheduledAt: string | undefined;

    if (trimmedDate && trimmedTime) {
      const composed = new Date(`${trimmedDate}T${trimmedTime}:00`);
      if (!Number.isNaN(composed.getTime())) {
        scheduledAt = composed.toISOString();
      }
    }

    const phoneDigits = values.telefone.replace(/\D/g, '');

    const payload: AppointmentCreateRequest = {
      nome_marca: values.nome_marca.trim(),
      nome_unidade: values.nome_unidade.trim(),
      nome_paciente: values.nome_paciente.trim(),
      tipo_consulta: values.tipo_consulta.trim() || undefined,
      cip: values.cip.trim() || undefined,
      status: values.status || DEFAULT_STATUS,
      telefone: phoneDigits,
      carro: values.carro.trim() || undefined,
      observacoes: values.observacoes.trim() || undefined,
      driver_id: values.driver_id || undefined,
      collector_id: values.collector_id || undefined,
      logistics_package_id: values.logistics_package_id || undefined,
      numero_convenio: values.numero_convenio.trim() || undefined,
      nome_convenio: values.nome_convenio.trim() || undefined,
      carteira_convenio: values.carteira_convenio.trim() || undefined,
      tags: values.tags ?? [],
    };

    if (scheduledAt) {
      payload.data_agendamento = scheduledAt;
    }

    if (trimmedTime) {
      payload.hora_agendamento = trimmedTime;
    }

    onSubmit(payload);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Adicionar Agendamento"
      size="xl"
    >
      <form className="space-y-6" onSubmit={handleSubmit(onSubmitForm)}>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Marca / Clínica *</label>
            <select
              {...register('nome_marca')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            >
              {brandOptions.map((brand) => (
                <option key={brand} value={brand}>
                  {brand}
                </option>
              ))}
            </select>
            {errors.nome_marca && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_marca.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Unidade *</label>
            <select
              {...register('nome_unidade')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            >
              {unitOptions.map((unit) => (
                <option key={unit} value={unit}>
                  {unit}
                </option>
              ))}
            </select>
            {errors.nome_unidade && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_unidade.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Nome do paciente *</label>
            <input
              type="text"
              {...register('nome_paciente')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Maria da Silva"
              disabled={isSubmitting}
            />
            {errors.nome_paciente && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_paciente.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Tipo de consulta</label>
            <input
              type="text"
              {...register('tipo_consulta')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Ex.: Coleta domiciliar"
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">CIP</label>
            <input
              type="text"
              {...register('cip')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Ex.: 123456"
              disabled={isSubmitting}
            />
            {errors.cip && (
              <p className="mt-1 text-sm text-red-600">{errors.cip.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Data</label>
            <input
              type="date"
              {...register('date')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
            {errors.date && (
              <p className="mt-1 text-sm text-red-600">{errors.date.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Hora</label>
            <input
              type="time"
              {...register('time')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
            {errors.time && (
              <p className="mt-1 text-sm text-red-600">{errors.time.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status *</label>
            <select
              {...register('status')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            >
              {statusChoices.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            {errors.status && (
              <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Telefone *</label>
            <input
              type="tel"
              {...register('telefone')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="1199998888"
              disabled={isSubmitting}
            />
            {errors.telefone && (
              <p className="mt-1 text-sm text-red-600">{errors.telefone.message}</p>
            )}
          </div>
          {logisticsPackages.length > 0 && (
            <div className="md:col-span-3">
              <label className="block text-sm font-medium text-gray-700">Pacote logístico</label>
              <select
                {...register('logistics_package_id')}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={isSubmitting}
              >
                <option value="">Sem pacote pré-definido</option>
                {logisticsPackages.map((logisticsPackage) => (
                  <option key={logisticsPackage.id} value={logisticsPackage.id}>
                    {logisticsPackage.nome}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Selecionar um pacote preenche automaticamente motorista, coletora e carro. Os campos podem ser ajustados após a seleção.
              </p>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700">Motorista</label>
            <select
              {...register('driver_id')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            >
              <option value="">Sem motorista</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.nome_completo}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Coletora</label>
            <select
              {...register('collector_id')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            >
              <option value="">Sem coletora</option>
              {collectors.map((collector) => (
                <option key={collector.id} value={collector.id}>
                  {collector.nome_completo}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Carro</label>
            <input
              type="text"
              {...register('carro')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Placa ou identificação"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Nome do convênio</label>
            <input
              type="text"
              {...register('nome_convenio')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Número do convênio</label>
            <input
              type="text"
              {...register('numero_convenio')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-700">Carteira do convênio</label>
            <input
              type="text"
              {...register('carteira_convenio')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Observações</label>
            <textarea
              rows={3}
              {...register('observacoes')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Informações adicionais relevantes"
              disabled={isSubmitting}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Tags</label>
          <p className="mt-1 text-xs text-gray-500">
            Selecione até {maxTags} tags para facilitar a identificação do agendamento.
          </p>
          <div className="mt-3">
            <Controller
              control={control}
              name="tags"
              render={({ field }) => (
                <TagSelector
                  availableTags={tags}
                  selectedTagIds={field.value}
                  onChange={field.onChange}
                  disabled={isSubmitting}
                  maxSelected={maxTags}
                />
              )}
            />
            {errors.tags && (
              <p className="mt-1 text-sm text-red-600">{errors.tags.message}</p>
            )}
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={handleClose}
            className="inline-flex justify-center rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Salvando...' : 'Salvar agendamento'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
