import { useEffect } from 'react';
import { type SubmitHandler, useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import { Modal } from './ui/Modal';
import type { Client } from '../types/client';

interface ClientFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ClientFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  client?: Client;
  serverError?: string | null;
}

const formSchema = z.object({
  nome: z.string().trim().min(1, 'Informe o nome do cliente'),
  cpf: z
    .string()
    .trim()
    .min(1, 'Informe o CPF do cliente')
    .refine((value) => value.replace(/\D/g, '').length === 11, 'CPF deve conter 11 dígitos'),
  telefone: z
    .string()
    .optional()
    .transform((value) => (value ? value.trim() : ''))
    .refine((value) => {
      if (!value) return true;
      const digits = value.replace(/\D/g, '');
      return digits.length === 10 || digits.length === 11;
    }, 'Telefone deve conter 10 ou 11 dígitos')
    .default(''),
  email: z
    .string()
    .optional()
    .transform((value) => (value ? value.trim() : ''))
    .refine((value) => {
      if (!value) return true;
      return /\S+@\S+\.\S+/.test(value);
    }, 'Informe um email válido')
    .default(''),
  observacoes: z.string().optional().transform((value) => value?.trim() ?? '').default(''),
});

export type ClientFormValues = z.infer<typeof formSchema>;

export function ClientFormModal({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  client,
  serverError,
}: ClientFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ClientFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      nome: '',
      cpf: '',
      telefone: '',
      email: '',
      observacoes: '',
    },
  });

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (client) {
      reset({
        nome: client.nome,
        cpf: client.cpf,
        telefone: client.telefone ?? '',
        email: client.email ?? '',
        observacoes: client.observacoes ?? '',
      });
    } else {
      reset({
        nome: '',
        cpf: '',
        telefone: '',
        email: '',
        observacoes: '',
      });
    }
  }, [client, isOpen, reset]);

  const onSubmitForm: SubmitHandler<ClientFormValues> = (values) => {
    const phoneDigits = values.telefone ? values.telefone.replace(/\D/g, '') : undefined;
    const cpfDigits = values.cpf.replace(/\D/g, '');

    onSubmit({
      nome: values.nome.trim(),
      cpf: cpfDigits,
      telefone: phoneDigits ?? '',
      email: values.email || '',
      observacoes: values.observacoes || '',
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={client ? 'Editar Cliente' : 'Novo Cliente'}
      size="md"
    >
      <form className="space-y-4" onSubmit={handleSubmit(onSubmitForm)}>
        <div>
          <label className="block text-sm font-medium text-gray-700">Nome *</label>
          <input
            type="text"
            {...register('nome')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Nome completo"
            disabled={isSubmitting}
          />
          {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">CPF *</label>
          <input
            type="text"
            {...register('cpf')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="00000000000"
            disabled={isSubmitting || Boolean(client)}
          />
          {errors.cpf && <p className="mt-1 text-sm text-red-600">{errors.cpf.message}</p>}
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Telefone</label>
            <input
              type="tel"
              {...register('telefone')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="11999999999"
              disabled={isSubmitting}
            />
            {errors.telefone && (
              <p className="mt-1 text-sm text-red-600">{errors.telefone.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              {...register('email')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="email@dominio.com"
              disabled={isSubmitting}
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Observações</label>
          <textarea
            rows={4}
            {...register('observacoes')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Informações relevantes, preferências, etc."
            disabled={isSubmitting}
          />
        </div>

        {serverError && (
          <p className="text-sm text-red-600" role="alert">
            {serverError}
          </p>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="inline-flex items-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {client ? 'Salvar alterações' : 'Cadastrar cliente'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
