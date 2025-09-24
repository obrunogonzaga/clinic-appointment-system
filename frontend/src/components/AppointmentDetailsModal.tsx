import { useEffect, useMemo, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { isAxiosError } from 'axios';
import { Modal } from './ui/Modal';
import { TagSelector } from './tags/TagSelector';
import { TagBadge } from './tags/TagBadge';
import { useAppointmentDetails, useUpdateAppointment } from '../hooks/useAppointmentDetails';
import { APPOINTMENT_STATUS_OPTIONS } from '../utils/appointmentViewModel';
import { formatDate } from '../utils/dateUtils';
import { getStatusBadgeClass } from '../utils/statusColors';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import type { Tag } from '../types/tag';
import type { AppointmentUpdateRequest } from '../types/appointment';

interface AppointmentDetailsModalProps {
  appointmentId: string | null;
  isOpen: boolean;
  onClose: () => void;
  drivers: ActiveDriver[];
  collectors: ActiveCollector[];
  statuses?: string[];
  tags: Tag[];
  maxTags?: number;
  onEditSuccess?: (message: string) => void;
  onEditError?: (message: string) => void;
}

type FormValues = {
  status: string;
  telefone: string;
  observacoes: string;
  driver_id: string;
  collector_id: string;
  tags: string[];
  nome_unidade: string;
  nome_marca: string;
  nome_paciente: string;
  tipo_consulta: string;
  cip: string;
  carro: string;
  numero_convenio: string;
  nome_convenio: string;
  carteira_convenio: string;
  canal_confirmacao: string;
  data_confirmacao_date: string;
  data_confirmacao_time: string;
  data_agendamento_date: string;
  data_agendamento_time: string;
  endereco_rua: string;
  endereco_numero: string;
  endereco_complemento: string;
  endereco_bairro: string;
  endereco_cidade: string;
  endereco_estado: string;
  endereco_cep: string;
  cpf: string;
  rg: string;
};

type TagSummary = Pick<Tag, 'id' | 'name' | 'color'>;

type DetailItem = {
  label: string;
  value?: string;
  variant?: 'status' | 'multiline' | 'tags';
  tags?: TagSummary[];
};

type DetailGroup = {
  key: string;
  title: string;
  items: DetailItem[];
  columns?: 1 | 2 | 3;
};

const ensureValue = (value?: string | null): string => {
  if (value === undefined || value === null) {
    return '—';
  }

  const normalized = `${value}`.trim();
  return normalized.length > 0 ? normalized : '—';
};

const parseCarInfo = (rawCar?: string | null): string => {
  if (!rawCar) {
    return '—';
  }

  const match = /Carro:\s*([^|]+)/i.exec(rawCar);
  const label = match ? match[1] : rawCar;
  const normalized = label.trim();
  return normalized.length > 0 ? normalized : '—';
};

const toDateInputValue = (value?: string | null): string => {
  if (!value) {
    return '';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }

  return date.toISOString().slice(0, 10);
};

const toTimeInputValue = (value?: string | null): string => {
  if (!value) {
    return '';
  }

  const trimmed = value.trim();
  const match = trimmed.match(/^(\d{2}:\d{2})(?::\d{2})?/);
  if (match) {
    return match[1];
  }

  return '';
};

const normalizeDigits = (value: string): string => value.replace(/\D/g, '');

const toNullableString = (value: string): string | null => {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

const formatCpf = (digits: string): string => {
  if (digits.length !== 11) {
    return digits;
  }
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
};

const formatRg = (digits: string): string => {
  if (digits.length !== 9) {
    return digits;
  }
  return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}-${digits.slice(8)}`;
};

function areArraysEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  const sortedA = [...a].sort();
  const sortedB = [...b].sort();
  return sortedA.every((item, index) => item === sortedB[index]);
}

export function AppointmentDetailsModal({
  appointmentId,
  isOpen,
  onClose,
  drivers,
  collectors,
  statuses,
  tags,
  maxTags = 5,
  onEditSuccess,
  onEditError,
}: AppointmentDetailsModalProps) {
  const { data: appointment, isLoading, isError, error } = useAppointmentDetails(
    appointmentId
  );
  const {
    mutateAsync: updateAppointment,
    isPending: isUpdating,
  } = useUpdateAppointment();
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('appointment');

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      status: '',
      telefone: '',
      observacoes: '',
      driver_id: '',
      collector_id: '',
      tags: [],
      nome_unidade: '',
      nome_marca: '',
      nome_paciente: '',
      tipo_consulta: '',
      cip: '',
      carro: '',
      numero_convenio: '',
      nome_convenio: '',
      carteira_convenio: '',
      canal_confirmacao: '',
      data_confirmacao_date: '',
      data_confirmacao_time: '',
      data_agendamento_date: '',
      data_agendamento_time: '',
      endereco_rua: '',
      endereco_numero: '',
      endereco_complemento: '',
      endereco_bairro: '',
      endereco_cidade: '',
      endereco_estado: '',
      endereco_cep: '',
      cpf: '',
      rg: '',
    },
  });

  const statusOptions = useMemo(
    () => (statuses && statuses.length > 0 ? statuses : APPOINTMENT_STATUS_OPTIONS),
    [statuses]
  );

  useEffect(() => {
    if (appointment) {
      const appointmentDate = toDateInputValue(appointment.data_agendamento);
      const confirmationDate = toDateInputValue(appointment.data_confirmacao);
      const confirmationTime = appointment.hora_confirmacao
        ? toTimeInputValue(appointment.hora_confirmacao)
        : toTimeInputValue(appointment.data_confirmacao?.split('T')[1]);
      const cpfFormatted = appointment.documento_normalizado?.cpf_formatted
        ?? (appointment.cpf ? formatCpf(appointment.cpf) : '');
      const rgFormatted = appointment.documento_normalizado?.rg_formatted
        ?? (appointment.rg ? formatRg(appointment.rg) : '');

      reset({
        status: appointment.status,
        telefone: appointment.telefone ?? '',
        observacoes: appointment.observacoes ?? '',
        driver_id: appointment.driver_id ?? '',
        collector_id: appointment.collector_id ?? '',
        tags: (appointment.tags ?? []).map((tagItem) => tagItem.id),
        nome_unidade: appointment.nome_unidade ?? '',
        nome_marca: appointment.nome_marca ?? '',
        nome_paciente: appointment.nome_paciente ?? '',
        tipo_consulta: appointment.tipo_consulta ?? '',
        cip: appointment.cip ?? '',
        carro: appointment.carro ?? '',
        numero_convenio: appointment.numero_convenio ?? '',
        nome_convenio: appointment.nome_convenio ?? '',
        carteira_convenio: appointment.carteira_convenio ?? '',
        canal_confirmacao: appointment.canal_confirmacao ?? '',
        data_confirmacao_date: confirmationDate,
        data_confirmacao_time: confirmationTime,
        data_agendamento_date: appointmentDate,
        data_agendamento_time: appointment.hora_agendamento ?? '',
        endereco_rua: appointment.endereco_normalizado?.rua ?? '',
        endereco_numero: appointment.endereco_normalizado?.numero ?? '',
        endereco_complemento: appointment.endereco_normalizado?.complemento ?? '',
        endereco_bairro: appointment.endereco_normalizado?.bairro ?? '',
        endereco_cidade: appointment.endereco_normalizado?.cidade ?? '',
        endereco_estado: appointment.endereco_normalizado?.estado ?? '',
        endereco_cep: appointment.endereco_normalizado?.cep ?? appointment.cep ?? '',
        cpf: cpfFormatted,
        rg: rgFormatted,
      });
    }
  }, [appointment, reset]);

  useEffect(() => {
    if (!isOpen) {
      setIsEditing(false);
      setActiveTab('appointment');
    }
  }, [isOpen]);

  const handleClose = () => {
    setIsEditing(false);
    onClose();
  };

  const onSubmit = handleSubmit(async (values) => {
    if (!appointmentId || !appointment) {
      return;
    }

    const payload: AppointmentUpdateRequest = {};

    type UpdatableTextField =
      | 'status'
      | 'observacoes'
      | 'nome_unidade'
      | 'nome_marca'
      | 'nome_paciente'
      | 'tipo_consulta'
      | 'cip'
      | 'carro'
      | 'numero_convenio'
      | 'nome_convenio'
      | 'carteira_convenio'
      | 'canal_confirmacao';

    const assignStringField = <Field extends UpdatableTextField>(
      field: Field,
      newValue: string,
      originalValue?: string | null
    ) => {
      const normalizedOriginal = (originalValue ?? '').trim();
      const normalizedNew = newValue.trim();

      if (normalizedNew !== normalizedOriginal) {
        const result = normalizedNew.length > 0 ? normalizedNew : null;
        payload[field] = result as AppointmentUpdateRequest[Field];
      }
    };

    assignStringField('status', values.status, appointment.status);

    const normalizedPhone = normalizeDigits(values.telefone);
    if (normalizedPhone !== (appointment.telefone ?? '')) {
      payload.telefone = normalizedPhone || null;
    }

    assignStringField('observacoes', values.observacoes, appointment.observacoes);
    assignStringField('nome_unidade', values.nome_unidade, appointment.nome_unidade);
    assignStringField('nome_marca', values.nome_marca, appointment.nome_marca);
    assignStringField('nome_paciente', values.nome_paciente, appointment.nome_paciente);
    assignStringField('tipo_consulta', values.tipo_consulta, appointment.tipo_consulta);
    assignStringField('cip', values.cip, appointment.cip);
    assignStringField('carro', values.carro, appointment.carro);
    assignStringField('numero_convenio', values.numero_convenio, appointment.numero_convenio);
    assignStringField('nome_convenio', values.nome_convenio, appointment.nome_convenio);
    assignStringField('carteira_convenio', values.carteira_convenio, appointment.carteira_convenio);
    assignStringField('canal_confirmacao', values.canal_confirmacao, appointment.canal_confirmacao);

    const driverId = values.driver_id || null;
    if (driverId !== (appointment.driver_id ?? null)) {
      payload.driver_id = driverId;
    }

    const collectorId = values.collector_id || null;
    if (collectorId !== (appointment.collector_id ?? null)) {
      payload.collector_id = collectorId;
    }

    const currentTagIds = (appointment.tags ?? []).map((tagItem) => tagItem.id);
    if (!areArraysEqual(values.tags, currentTagIds)) {
      payload.tags = values.tags;
    }

    const originalDate = toDateInputValue(appointment.data_agendamento);
    const originalTime = appointment.hora_agendamento ?? '';
    const newDate = values.data_agendamento_date.trim();
    const newTime = values.data_agendamento_time.trim();

    if (newDate !== originalDate || newTime !== originalTime) {
      if (newDate) {
        const timePart = newTime || '00:00';
        const composed = new Date(`${newDate}T${timePart}:00`);
        if (!Number.isNaN(composed.getTime())) {
          payload.data_agendamento = composed.toISOString();
          payload.hora_agendamento = timePart;
        }
      }
    }

    const originalConfirmationDate = toDateInputValue(appointment.data_confirmacao);
    const originalConfirmationTime = appointment.hora_confirmacao
      ? toTimeInputValue(appointment.hora_confirmacao)
      : '';
    const newConfirmationDate = values.data_confirmacao_date.trim();
    const newConfirmationTime = values.data_confirmacao_time.trim();

    if (
      newConfirmationDate !== originalConfirmationDate ||
      newConfirmationTime !== originalConfirmationTime
    ) {
      if (newConfirmationDate) {
        const confirmationIso = new Date(
          `${newConfirmationDate}T${(newConfirmationTime || '00:00')}:00`
        );
        if (!Number.isNaN(confirmationIso.getTime())) {
          payload.data_confirmacao = confirmationIso.toISOString();
          payload.hora_confirmacao = newConfirmationTime || null;
        }
      } else {
        payload.data_confirmacao = null;
        payload.hora_confirmacao = null;
      }
    }

    const newAddress = {
      rua: toNullableString(values.endereco_rua),
      numero: toNullableString(values.endereco_numero),
      complemento: toNullableString(values.endereco_complemento),
      bairro: toNullableString(values.endereco_bairro),
      cidade: toNullableString(values.endereco_cidade),
      estado: toNullableString(values.endereco_estado),
      cep: toNullableString(values.endereco_cep),
    };

    const originalAddress = {
      rua: appointment.endereco_normalizado?.rua ?? null,
      numero: appointment.endereco_normalizado?.numero ?? null,
      complemento: appointment.endereco_normalizado?.complemento ?? null,
      bairro: appointment.endereco_normalizado?.bairro ?? null,
      cidade: appointment.endereco_normalizado?.cidade ?? null,
      estado: appointment.endereco_normalizado?.estado ?? null,
      cep: appointment.endereco_normalizado?.cep ?? appointment.cep ?? null,
    };

    if (JSON.stringify(newAddress) !== JSON.stringify(originalAddress)) {
      payload.endereco_normalizado = newAddress;
      // Preserve legacy CEP field as well when address changes
      payload.cep = newAddress.cep ?? null;
    }

    const newCpfDigits = normalizeDigits(values.cpf);
    const newRgDigits = normalizeDigits(values.rg);
    const originalCpfDigits = appointment.cpf ?? '';
    const originalRgDigits = appointment.rg ?? '';

    if (newCpfDigits !== originalCpfDigits) {
      payload.cpf = newCpfDigits || null;
    }

    if (newRgDigits !== originalRgDigits) {
      payload.rg = newRgDigits || null;
    }

    const newDocumentNormalized = {
      cpf: newCpfDigits ? newCpfDigits : null,
      rg: newRgDigits ? newRgDigits : null,
      cpf_formatted: newCpfDigits ? formatCpf(newCpfDigits) : null,
      rg_formatted: newRgDigits ? formatRg(newRgDigits) : null,
    };

    const originalDocumentNormalized = {
      cpf:
        appointment.documento_normalizado?.cpf ??
        (appointment.cpf ? appointment.cpf : null),
      rg:
        appointment.documento_normalizado?.rg ??
        (appointment.rg ? appointment.rg : null),
      cpf_formatted:
        appointment.documento_normalizado?.cpf_formatted ??
        (appointment.cpf ? formatCpf(appointment.cpf) : null),
      rg_formatted:
        appointment.documento_normalizado?.rg_formatted ??
        (appointment.rg ? formatRg(appointment.rg) : null),
    };

    if (
      JSON.stringify(newDocumentNormalized) !==
      JSON.stringify(originalDocumentNormalized)
    ) {
      payload.documento_normalizado = newDocumentNormalized;
    }

    if (Object.keys(payload).length === 0) {
      setIsEditing(false);
      onEditSuccess?.('Nenhuma alteração para salvar.');
      return;
    }

    try {
      const updated = await updateAppointment({
        appointmentId,
        data: payload,
      });

      reset({
        status: updated.status,
        telefone: updated.telefone ?? '',
        observacoes: updated.observacoes ?? '',
        driver_id: updated.driver_id ?? '',
        collector_id: updated.collector_id ?? '',
        tags: (updated.tags ?? []).map((tagItem) => tagItem.id),
        nome_unidade: updated.nome_unidade ?? '',
        nome_marca: updated.nome_marca ?? '',
        nome_paciente: updated.nome_paciente ?? '',
        tipo_consulta: updated.tipo_consulta ?? '',
        cip: updated.cip ?? '',
        carro: updated.carro ?? '',
        numero_convenio: updated.numero_convenio ?? '',
        nome_convenio: updated.nome_convenio ?? '',
        carteira_convenio: updated.carteira_convenio ?? '',
        canal_confirmacao: updated.canal_confirmacao ?? '',
        data_confirmacao_date: toDateInputValue(updated.data_confirmacao),
        data_confirmacao_time: updated.hora_confirmacao
          ? toTimeInputValue(updated.hora_confirmacao)
          : toTimeInputValue(updated.data_confirmacao?.split('T')[1]),
        data_agendamento_date: toDateInputValue(updated.data_agendamento),
        data_agendamento_time: updated.hora_agendamento ?? '',
        endereco_rua: updated.endereco_normalizado?.rua ?? '',
        endereco_numero: updated.endereco_normalizado?.numero ?? '',
        endereco_complemento: updated.endereco_normalizado?.complemento ?? '',
        endereco_bairro: updated.endereco_normalizado?.bairro ?? '',
        endereco_cidade: updated.endereco_normalizado?.cidade ?? '',
        endereco_estado: updated.endereco_normalizado?.estado ?? '',
        endereco_cep: updated.endereco_normalizado?.cep ?? updated.cep ?? '',
        cpf:
          updated.documento_normalizado?.cpf_formatted ??
          (updated.cpf ? formatCpf(updated.cpf) : ''),
        rg:
          updated.documento_normalizado?.rg_formatted ??
          (updated.rg ? formatRg(updated.rg) : ''),
      });

      setIsEditing(false);
      onEditSuccess?.('Agendamento atualizado com sucesso.');
    } catch (mutationError) {
      if (isAxiosError(mutationError)) {
        const message =
          (mutationError.response?.data as { detail?: string; message?: string } | undefined)?.detail ||
          mutationError.message ||
          'Não foi possível atualizar o agendamento.';
        onEditError?.(typeof message === 'string' ? message : 'Não foi possível atualizar o agendamento.');
      } else {
        onEditError?.('Não foi possível atualizar o agendamento.');
      }
    }
  });

  const detailGroups = useMemo<DetailGroup[]>(() => {
    if (!appointment) {
      return [];
    }

    const carInfo = parseCarInfo(appointment.carro);
    const cpfValue = ensureValue(
      appointment.documento_normalizado?.cpf_formatted ?? appointment.cpf
    );
    const rgValue = ensureValue(
      appointment.documento_normalizado?.rg_formatted ?? appointment.rg
    );
    const confirmationDateLabel = appointment.data_confirmacao
      ? formatDate(appointment.data_confirmacao)
      : '—';

    const driverName = appointment.driver_id
      ? ensureValue(
          drivers.find((driver) => driver.id === appointment.driver_id)?.nome_completo
        )
      : 'Não atribuído';

    const collectorName = appointment.collector_id
      ? ensureValue(
          collectors.find((collector) => collector.id === appointment.collector_id)?.nome_completo
        )
      : 'Não atribuída';

    const normalizedAddressItems: DetailItem[] = [
      { label: 'Rua', value: ensureValue(appointment.endereco_normalizado?.rua) },
      { label: 'Número', value: ensureValue(appointment.endereco_normalizado?.numero) },
      { label: 'Complemento', value: ensureValue(appointment.endereco_normalizado?.complemento) },
      { label: 'Bairro', value: ensureValue(appointment.endereco_normalizado?.bairro) },
      { label: 'Cidade', value: ensureValue(appointment.endereco_normalizado?.cidade) },
      { label: 'Estado', value: ensureValue(appointment.endereco_normalizado?.estado) },
      {
        label: 'CEP',
        value: ensureValue(
          appointment.endereco_normalizado?.cep ?? appointment.cep
        ),
      },
    ];

    const hasNormalizedAddress = normalizedAddressItems.some(
      (item) => item.value !== '—'
    );

    const groups: DetailGroup[] = [
      {
        key: 'appointment',
        title: 'Informações do agendamento',
        items: [
          { label: 'Nome da unidade', value: ensureValue(appointment.nome_unidade) },
          { label: 'Nome da marca', value: ensureValue(appointment.nome_marca) },
          { label: 'Nome do paciente', value: ensureValue(appointment.nome_paciente) },
          { label: 'Tipo de consulta', value: ensureValue(appointment.tipo_consulta) },
          { label: 'CIP', value: ensureValue(appointment.cip) },
          { label: 'Data do agendamento', value: formatDate(appointment.data_agendamento ?? '') },
          { label: 'Hora do agendamento', value: ensureValue(appointment.hora_agendamento) },
          { label: 'Status', value: ensureValue(appointment.status), variant: 'status' },
          { label: 'Carro', value: carInfo },
        ],
      },
      {
        key: 'contact',
        title: 'Contato e convênio',
        items: [
          { label: 'Telefone', value: ensureValue(appointment.telefone) },
          {
            label: 'Observações',
            value: ensureValue(appointment.observacoes),
            variant: 'multiline',
          },
          { label: 'Número do convênio', value: ensureValue(appointment.numero_convenio) },
          { label: 'Nome do convênio', value: ensureValue(appointment.nome_convenio) },
          { label: 'Carteira do convênio', value: ensureValue(appointment.carteira_convenio) },
          {
            label: 'Tags',
            variant: 'tags',
            tags: appointment.tags ?? [],
          },
        ],
      },
      {
        key: 'documents',
        title: 'Documentos do paciente',
        items: [
          { label: 'CPF', value: cpfValue },
          { label: 'RG', value: rgValue },
        ],
      },
      {
        key: 'team',
        title: 'Equipe designada',
        items: [
          { label: 'Motorista', value: driverName },
          { label: 'Coletora', value: collectorName },
        ],
      },
    ];

    if (hasNormalizedAddress) {
      groups.push({
        key: 'address',
        title: 'Endereço normalizado',
        items: normalizedAddressItems,
        columns: 3,
      });
    }

    groups.push({
      key: 'confirmation',
      title: 'Confirmação',
      items: [
        {
          label: 'Canal de confirmação',
          value: ensureValue(appointment.canal_confirmacao),
        },
        {
          label: 'Data de confirmação',
          value: confirmationDateLabel,
        },
        {
          label: 'Hora de confirmação',
          value: ensureValue(appointment.hora_confirmacao),
        },
      ],
    });

    return groups;
  }, [appointment, collectors, drivers]);

  useEffect(() => {
    if (detailGroups.length === 0) {
      return;
    }

    setActiveTab((previous) =>
      detailGroups.some((group) => group.key === previous)
        ? previous
        : detailGroups[0].key
    );
  }, [detailGroups]);

  const renderValue = (item: DetailItem) => {
    if (item.variant === 'tags') {
      if (!item.tags || item.tags.length === 0) {
        return <p className="mt-1 text-sm text-gray-700">—</p>;
      }

      return (
        <div className="mt-1 flex flex-wrap gap-2">
          {item.tags.map((tagItem) => (
            <TagBadge
              key={tagItem.id}
              name={tagItem.name}
              color={tagItem.color}
              size="sm"
            />
          ))}
        </div>
      );
    }

    if (item.variant === 'status') {
      const statusValue = item.value;
      if (!statusValue || statusValue === '—') {
        return <p className="mt-1 text-sm text-gray-700">—</p>;
      }

      return (
        <span className={`${getStatusBadgeClass(statusValue)} mt-1 inline-flex items-center`}>
          {statusValue}
        </span>
      );
    }

    if (item.variant === 'multiline') {
      return (
        <p className="mt-1 whitespace-pre-line text-sm text-gray-700">
          {item.value}
        </p>
      );
    }

    return (
      <p className="mt-1 text-sm text-gray-700">
        {item.value}
      </p>
    );
  };

  const renderHeader = (showEditButton: boolean) => {
    if (!appointment) {
      return null;
    }

    return (
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {ensureValue(appointment.nome_paciente)}
          </h2>
          <p className="text-sm text-gray-500">
            {ensureValue(appointment.nome_marca)} • {ensureValue(appointment.nome_unidade)}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs font-medium uppercase tracking-wide text-gray-500">
            {appointment.status?.trim() ? (
              <span
                className={`${getStatusBadgeClass(
                  appointment.status
                )} inline-flex items-center`}
              >
                {appointment.status}
              </span>
            ) : (
              <span>—</span>
            )}
            <span>{formatDate(appointment.data_agendamento ?? '')}</span>
            <span>{ensureValue(appointment.hora_agendamento)}</span>
          </div>
        </div>
        {showEditButton ? (
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Editar
          </button>
        ) : null}
      </div>
    );
  };

  const resolveColumnsClass = (count?: 1 | 2 | 3) => {
    if (count === 1) {
      return 'md:grid-cols-1';
    }
    if (count === 3) {
      return 'md:grid-cols-3';
    }
    return 'md:grid-cols-2';
  };

  const renderTabNavigation = (groups: DetailGroup[]) => {
    if (groups.length === 0) {
      return null;
    }

    return (
      <div className="mt-6 flex flex-wrap gap-2 border-b border-gray-200 pb-2">
        {groups.map((group) => {
          const isActive = activeTab === group.key;
          return (
            <button
              key={group.key}
              type="button"
              onClick={() => setActiveTab(group.key)}
              className={`rounded-full px-3 py-1 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {group.title}
            </button>
          );
        })}
      </div>
    );
  };

  const renderReadTabContent = () => {
    if (detailGroups.length === 0) {
      return null;
    }

    const current =
      detailGroups.find((group) => group.key === activeTab) ?? detailGroups[0];

    return (
      <section className="mt-4">
        <div
          className={`grid grid-cols-1 gap-4 ${resolveColumnsClass(
            current.columns
          )}`}
        >
          {current.items.map((item) => (
            <div key={`${current.key}-${item.label}`}>
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {item.label}
              </p>
              {renderValue(item)}
            </div>
          ))}
        </div>
      </section>
    );
  };

  const renderEditTabContent = () => {
    switch (activeTab) {
      case 'appointment':
        return (
          <section className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Nome da unidade
                </label>
                <input
                  type="text"
                  {...register('nome_unidade', { required: 'Informe a unidade' })}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
                {errors.nome_unidade && (
                  <p className="mt-1 text-xs text-red-600">{errors.nome_unidade.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Nome da marca
                </label>
                <input
                  type="text"
                  {...register('nome_marca', { required: 'Informe a marca' })}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
                {errors.nome_marca && (
                  <p className="mt-1 text-xs text-red-600">{errors.nome_marca.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Nome do paciente
                </label>
                <input
                  type="text"
                  {...register('nome_paciente', {
                    required: 'Informe o nome do paciente',
                  })}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
                {errors.nome_paciente && (
                  <p className="mt-1 text-xs text-red-600">{errors.nome_paciente.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Tipo de consulta
                </label>
                <input
                  type="text"
                  {...register('tipo_consulta')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  CIP
                </label>
                <input
                  type="text"
                  {...register('cip')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Carro
                </label>
                <input
                  type="text"
                  {...register('carro')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Data do agendamento
                </label>
                <input
                  type="date"
                  {...register('data_agendamento_date')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Hora do agendamento
                </label>
                <input
                  type="time"
                  step="60"
                  {...register('data_agendamento_time')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Status
                </label>
                <select
                  {...register('status', { required: 'Selecione um status' })}
                  className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                >
                  {statusOptions.map((statusOption) => (
                    <option key={statusOption} value={statusOption}>
                      {statusOption}
                    </option>
                  ))}
                </select>
                {errors.status && (
                  <p className="mt-1 text-xs text-red-600">{errors.status.message}</p>
                )}
              </div>
            </div>
          </section>
        );

      case 'contact':
        return (
          <section className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Telefone
                </label>
                <input
                  type="tel"
                  {...register('telefone', {
                    validate: (value) => {
                      const digits = normalizeDigits(value);
                      if (!digits) {
                        return true;
                      }
                      return (
                        digits.length === 10 ||
                        digits.length === 11 ||
                        'Informe um telefone válido com DDD.'
                      );
                    },
                  })}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
                {errors.telefone && (
                  <p className="mt-1 text-xs text-red-600">{errors.telefone.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Número do convênio
                </label>
                <input
                  type="text"
                  {...register('numero_convenio')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Nome do convênio
                </label>
                <input
                  type="text"
                  {...register('nome_convenio')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Carteira do convênio
                </label>
                <input
                  type="text"
                  {...register('carteira_convenio')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Observações
              </label>
              <textarea
                {...register('observacoes')}
                rows={4}
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isUpdating}
              />
            </div>

            <div>
              <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                Tags
              </label>
              <Controller
                control={control}
                name="tags"
                render={({ field }) => (
                  <TagSelector
                    availableTags={tags}
                    selectedTagIds={field.value}
                    onChange={field.onChange}
                    disabled={isUpdating}
                    maxSelected={maxTags}
                  />
                )}
              />
            </div>
          </section>
        );

      case 'documents':
        return (
          <section className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  CPF
                </label>
                <input
                  type="text"
                  {...register('cpf')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  RG
                </label>
                <input
                  type="text"
                  {...register('rg')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
            </div>
          </section>
        );

      case 'team':
        return (
          <section className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Motorista
                </label>
                <select
                  {...register('driver_id')}
                  className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                >
                  <option value="">Selecione um motorista</option>
                  {drivers.map((driver) => (
                    <option key={driver.id} value={driver.id}>
                      {driver.nome_completo}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Coletora
                </label>
                <select
                  {...register('collector_id')}
                  className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                >
                  <option value="">Selecione uma coletora</option>
                  {collectors.map((collector) => (
                    <option key={collector.id} value={collector.id}>
                      {collector.nome_completo}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </section>
        );

      case 'address':
        return (
          <section className="mt-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Rua
                </label>
                <input
                  type="text"
                  {...register('endereco_rua')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Número
                </label>
                <input
                  type="text"
                  {...register('endereco_numero')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Complemento
                </label>
                <input
                  type="text"
                  {...register('endereco_complemento')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Bairro
                </label>
                <input
                  type="text"
                  {...register('endereco_bairro')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Cidade
                </label>
                <input
                  type="text"
                  {...register('endereco_cidade')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Estado
                </label>
                <input
                  type="text"
                  {...register('endereco_estado')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  CEP
                </label>
                <input
                  type="text"
                  {...register('endereco_cep')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
            </div>
          </section>
        );

      case 'confirmation':
        return (
          <section className="mt-4 space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Canal de confirmação
                </label>
                <input
                  type="text"
                  {...register('canal_confirmacao')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Data da confirmação
                </label>
                <input
                  type="date"
                  {...register('data_confirmacao_date')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>

              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Hora da confirmação
                </label>
                <input
                  type="time"
                  step="60"
                  {...register('data_confirmacao_time')}
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                />
              </div>
            </div>
          </section>
        );

      default:
        return null;
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Detalhes do agendamento"
      size="xl"
    >
      {isLoading && (
        <div className="py-8 text-center text-sm text-gray-500">
          Carregando informações do agendamento...
        </div>
      )}

      {isError && (
        <div className="py-8 text-center text-sm text-red-600">
          {error instanceof Error
            ? error.message
            : 'Não foi possível carregar os detalhes do agendamento.'}
        </div>
      )}

      {!isLoading && !isError && appointment && !isEditing && (
        <>
          {renderHeader(true)}
          {renderTabNavigation(detailGroups)}
          {renderReadTabContent()}
        </>
      )}

      {!isLoading && !isError && appointment && isEditing && (
        <form className="space-y-6" onSubmit={onSubmit}>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Editar {appointment.nome_paciente}
              </h2>
              <p className="text-sm text-gray-500">
                Atualize os campos necessários nas abas abaixo.
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  if (!appointment) {
                    return;
                  }
                  const appointmentDate = toDateInputValue(appointment.data_agendamento);
                  const confirmationDate = toDateInputValue(appointment.data_confirmacao);
                  const confirmationTime = appointment.hora_confirmacao
                    ? toTimeInputValue(appointment.hora_confirmacao)
                    : toTimeInputValue(appointment.data_confirmacao?.split('T')[1]);
                  const cpfFormatted = appointment.documento_normalizado?.cpf_formatted
                    ?? (appointment.cpf ? formatCpf(appointment.cpf) : '');
                  const rgFormatted = appointment.documento_normalizado?.rg_formatted
                    ?? (appointment.rg ? formatRg(appointment.rg) : '');

                  reset({
                    status: appointment.status,
                    telefone: appointment.telefone ?? '',
                    observacoes: appointment.observacoes ?? '',
                    driver_id: appointment.driver_id ?? '',
                    collector_id: appointment.collector_id ?? '',
                    tags: (appointment.tags ?? []).map((tagItem) => tagItem.id),
                    nome_unidade: appointment.nome_unidade ?? '',
                    nome_marca: appointment.nome_marca ?? '',
                    nome_paciente: appointment.nome_paciente ?? '',
                    tipo_consulta: appointment.tipo_consulta ?? '',
                    cip: appointment.cip ?? '',
                    carro: appointment.carro ?? '',
                    numero_convenio: appointment.numero_convenio ?? '',
                    nome_convenio: appointment.nome_convenio ?? '',
                    carteira_convenio: appointment.carteira_convenio ?? '',
                    canal_confirmacao: appointment.canal_confirmacao ?? '',
                    data_confirmacao_date: confirmationDate,
                    data_confirmacao_time: confirmationTime,
                    data_agendamento_date: appointmentDate,
                    data_agendamento_time: appointment.hora_agendamento ?? '',
                    endereco_rua: appointment.endereco_normalizado?.rua ?? '',
                    endereco_numero: appointment.endereco_normalizado?.numero ?? '',
                    endereco_complemento: appointment.endereco_normalizado?.complemento ?? '',
                    endereco_bairro: appointment.endereco_normalizado?.bairro ?? '',
                    endereco_cidade: appointment.endereco_normalizado?.cidade ?? '',
                    endereco_estado: appointment.endereco_normalizado?.estado ?? '',
                    endereco_cep: appointment.endereco_normalizado?.cep ?? appointment.cep ?? '',
                    cpf: cpfFormatted,
                    rg: rgFormatted,
                  });
                  setIsEditing(false);
                  setActiveTab('appointment');
                }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isUpdating}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
                disabled={isUpdating}
              >
                {isUpdating ? 'Salvando...' : 'Salvar alterações'}
              </button>
            </div>
          </div>

          {renderTabNavigation(detailGroups)}
          {renderEditTabContent()}
        </form>
      )}
    </Modal>
  );
}
