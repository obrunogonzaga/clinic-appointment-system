import { useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { Modal } from './ui/Modal';
import type { AppointmentCreateRequest } from '../types/appointment';
import type { ActiveDriver } from '../types/driver';
import type { ActiveCollector } from '../types/collector';
import { APPOINTMENT_STATUS_OPTIONS } from '../utils/appointmentViewModel';

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
}

type FormValues = {
  nome_marca: string;
  nome_unidade: string;
  nome_paciente: string;
  date: string;
  time: string;
  tipo_consulta: string;
  status: string;
  telefone: string;
  carro: string;
  observacoes: string;
  driver_id: string;
  collector_id: string;
  numero_convenio: string;
  nome_convenio: string;
  carteira_convenio: string;
};

const formSchema = z.object({
  nome_marca: z.string().trim().min(1, 'Informe a marca/clinica'),
  nome_unidade: z.string().trim().min(1, 'Informe a unidade'),
  nome_paciente: z.string().trim().min(1, 'Informe o nome do paciente'),
  date: z.string().trim().min(1, 'Selecione a data do agendamento'),
  time: z
    .string()
    .trim()
    .regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Hora inválida (use HH:MM)'),
  tipo_consulta: z.string().trim().optional().default(''),
  status: z.string().trim().min(1, 'Selecione o status'),
  telefone: z
    .string()
    .trim()
    .min(1, 'Informe o telefone do paciente')
    .refine((value) => {
      const digits = value.replace(/\D/g, '');
      return digits.length === 10 || digits.length === 11;
    }, 'Telefone deve conter 10 ou 11 dígitos'),
  carro: z.string().trim().optional().default(''),
  observacoes: z.string().trim().optional().default(''),
  driver_id: z.string().trim().optional().default(''),
  collector_id: z.string().trim().optional().default(''),
  numero_convenio: z.string().trim().optional().default(''),
  nome_convenio: z.string().trim().optional().default(''),
  carteira_convenio: z.string().trim().optional().default(''),
});

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
}: AppointmentFormModalProps) {
  const statusChoices = useMemo(
    () => (statuses && statuses.length > 0 ? statuses : [...APPOINTMENT_STATUS_OPTIONS]),
    [statuses]
  );

  const defaultStatus = useMemo(() => {
    if (statusChoices.includes('Confirmado')) {
      return 'Confirmado';
    }
    if (statusChoices.includes('Agendado')) {
      return 'Agendado';
    }
    return statusChoices[0] ?? 'Pendente';
  }, [statusChoices]);

  const defaultValues = useMemo<FormValues>(
    () => ({
      nome_marca: '',
      nome_unidade: '',
      nome_paciente: '',
      date: '',
      time: '',
      tipo_consulta: '',
      status: defaultStatus,
      telefone: '',
      carro: '',
      observacoes: '',
      driver_id: '',
      collector_id: '',
      numero_convenio: '',
      nome_convenio: '',
      carteira_convenio: '',
    }),
    [defaultStatus]
  );

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues,
  });

  useEffect(() => {
    if (isOpen) {
      reset(defaultValues);
    }
  }, [isOpen, reset, defaultValues]);

  const handleClose = () => {
    reset(defaultValues);
    onClose();
  };

  const onSubmitForm = (values: FormValues) => {
    const iso = new Date(`${values.date}T${values.time}:00`);
    if (Number.isNaN(iso.getTime())) {
      return;
    }

    const phoneDigits = values.telefone.replace(/\D/g, '');

    const payload: AppointmentCreateRequest = {
      nome_marca: values.nome_marca.trim(),
      nome_unidade: values.nome_unidade.trim(),
      nome_paciente: values.nome_paciente.trim(),
      data_agendamento: iso.toISOString(),
      hora_agendamento: values.time,
      tipo_consulta: values.tipo_consulta.trim() || undefined,
      status: values.status,
      telefone: phoneDigits,
      carro: values.carro.trim() || undefined,
      observacoes: values.observacoes.trim() || undefined,
      driver_id: values.driver_id || undefined,
      collector_id: values.collector_id || undefined,
      numero_convenio: values.numero_convenio.trim() || undefined,
      nome_convenio: values.nome_convenio.trim() || undefined,
      carteira_convenio: values.carteira_convenio.trim() || undefined,
    };

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
            <input
              type="text"
              {...register('nome_marca')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              list="appointment-brand-options"
              placeholder="Clínica Saúde"
              disabled={isSubmitting}
            />
            <datalist id="appointment-brand-options">
              {brands.map((brand) => (
                <option key={brand} value={brand} />
              ))}
            </datalist>
            {errors.nome_marca && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_marca.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Unidade *</label>
            <input
              type="text"
              {...register('nome_unidade')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              list="appointment-unit-options"
              placeholder="Unidade Centro"
              disabled={isSubmitting}
            />
            <datalist id="appointment-unit-options">
              {units.map((unit) => (
                <option key={unit} value={unit} />
              ))}
            </datalist>
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
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Data *</label>
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
            <label className="block text-sm font-medium text-gray-700">Hora *</label>
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
