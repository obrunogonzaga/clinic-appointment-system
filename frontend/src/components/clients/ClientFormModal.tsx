import { useEffect, useMemo } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { Modal } from '../ui/Modal';
import type { ClientCreateRequest, ClientDetail, ClientUpdateRequest } from '../../types/client';
import { formatCpf, isValidCpf, normalizeCpf } from '../../utils/cpf';

const emptyStringSchema = z.string().trim().length(0);

const formSchema = z.object({
  nome_completo: z.string().trim().min(1, 'Informe o nome completo'),
  cpf: z
    .string()
    .trim()
    .min(1, 'Informe o CPF')
    .refine((value) => isValidCpf(value), 'CPF inválido. Verifique os dígitos.'),
  telefone: z.string().trim().optional(),
  email: z
    .union([emptyStringSchema, z.string().trim().email('E-mail inválido')])
    .optional(),
  observacoes: z.string().trim().optional(),
  numero_convenio: z.string().trim().optional(),
  nome_convenio: z.string().trim().optional(),
  carteira_convenio: z.string().trim().optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface ClientFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'create' | 'edit';
  onSubmit: (payload: ClientCreateRequest | ClientUpdateRequest) => Promise<void> | void;
  isSubmitting?: boolean;
  initialData?: ClientDetail | null;
}

const sanitizeOptional = (value?: string | null): string | undefined => {
  if (!value) {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
};

const normalizePhone = (value?: string | null): string | undefined => {
  if (!value) {
    return undefined;
  }
  const digits = value.replace(/\D/g, '');
  return digits ? digits : undefined;
};

export const ClientFormModal: React.FC<ClientFormModalProps> = ({
  isOpen,
  onClose,
  mode,
  onSubmit,
  isSubmitting = false,
  initialData,
}) => {
  const defaults = useMemo<FormValues>(() => {
    return {
      nome_completo: initialData?.nome_completo ?? '',
      cpf: initialData?.cpf ? formatCpf(initialData.cpf) : '',
      telefone: initialData?.telefone ?? '',
      email: initialData?.email ?? '',
      observacoes: initialData?.observacoes ?? '',
      numero_convenio: initialData?.numero_convenio ?? '',
      nome_convenio: initialData?.nome_convenio ?? '',
      carteira_convenio: initialData?.carteira_convenio ?? '',
    } as FormValues;
  }, [initialData]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: defaults,
  });

  useEffect(() => {
    if (isOpen) {
      reset(defaults);
    }
  }, [isOpen, defaults, reset]);

  const onSubmitForm: SubmitHandler<FormValues> = async (values) => {
    if (mode === 'create') {
      const payload: ClientCreateRequest = {
        nome_completo: values.nome_completo.trim(),
        cpf: normalizeCpf(values.cpf),
        telefone: normalizePhone(values.telefone),
        email: sanitizeOptional(values.email),
        observacoes: sanitizeOptional(values.observacoes),
        numero_convenio: sanitizeOptional(values.numero_convenio),
        nome_convenio: sanitizeOptional(values.nome_convenio),
        carteira_convenio: sanitizeOptional(values.carteira_convenio),
      };

      await onSubmit(payload);
      return;
    }

    const updatePayload: ClientUpdateRequest = {
      nome_completo: values.nome_completo.trim(),
      telefone: normalizePhone(values.telefone),
      email: sanitizeOptional(values.email),
      observacoes: sanitizeOptional(values.observacoes),
      numero_convenio: sanitizeOptional(values.numero_convenio),
      nome_convenio: sanitizeOptional(values.nome_convenio),
      carteira_convenio: sanitizeOptional(values.carteira_convenio),
    };

    await onSubmit(updatePayload);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === 'create' ? 'Cadastrar cliente' : 'Editar cliente'}
      size="lg"
    >
      <form className="space-y-5" onSubmit={handleSubmit(onSubmitForm)}>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nome completo *</label>
            <input
              type="text"
              {...register('nome_completo')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
            {errors.nome_completo && (
              <p className="mt-1 text-sm text-red-600">{errors.nome_completo.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">CPF *</label>
            <input
              type="text"
              {...register('cpf')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={mode === 'edit' || isSubmitting}
            />
            {errors.cpf && (
              <p className="mt-1 text-sm text-red-600">{errors.cpf.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Telefone</label>
            <input
              type="tel"
              {...register('telefone')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="11999988888"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">E-mail</label>
            <input
              type="email"
              {...register('email')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="cliente@exemplo.com"
              disabled={isSubmitting}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
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
          <div>
            <label className="block text-sm font-medium text-gray-700">Carteira do convênio</label>
            <input
              type="text"
              {...register('carteira_convenio')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              disabled={isSubmitting}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Observações</label>
          <textarea
            rows={4}
            {...register('observacoes')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Informações adicionais relevantes"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
          <button
            type="button"
            onClick={onClose}
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
            {isSubmitting ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
