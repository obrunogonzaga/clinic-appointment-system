import { zodResolver } from '@hookform/resolvers/zod';
import React, { useEffect, useMemo } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { z } from 'zod';
import type { Tag } from '../../types/tag';
import { Modal } from '../ui/Modal';

const formSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Informe um nome para a tag')
    .max(50, 'O nome deve ter no máximo 50 caracteres'),
  color: z
    .string()
    .trim()
    .regex(/^#([0-9a-fA-F]{6})$/, 'Selecione uma cor válida no formato #RRGGBB'),
  is_active: z.boolean().optional(),
});

export type TagFormValues = z.infer<typeof formSchema>;

interface TagFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: TagFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  initialData?: Tag | null;
}

export const TagFormModal: React.FC<TagFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
  initialData = null,
}) => {
  const defaultValues = useMemo<TagFormValues>(
    () => ({
      name: initialData?.name ?? '',
      color: initialData?.color ?? '#2563eb',
      is_active: initialData?.is_active ?? true,
    }),
    [initialData]
  );

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TagFormValues>({
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

  const handleFormSubmit = (values: TagFormValues) => {
    onSubmit({
      name: values.name.trim(),
      color: values.color.toLowerCase(),
      is_active: values.is_active,
    });
  };

  const showStatusToggle = Boolean(initialData);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={initialData ? 'Editar tag' : 'Nova tag'}
      size="sm"
    >
      <form className="space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Nome da tag *
          </label>
          <input
            type="text"
            {...register('name')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Ex.: Urgente"
            maxLength={50}
            disabled={isSubmitting}
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cor da tag *
          </label>
          <div className="mt-2 flex items-center gap-3">
            <Controller
              control={control}
              name="color"
              render={({ field }) => (
                <>
                  <input
                    type="color"
                    value={field.value}
                    onChange={(event) => field.onChange(event.target.value)}
                    disabled={isSubmitting}
                    className="h-10 w-16 cursor-pointer rounded-md border border-gray-200"
                    aria-label="Escolher cor"
                  />
                  <input
                    type="text"
                    value={field.value}
                    onChange={(event) => field.onChange(event.target.value)}
                    className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="#2563eb"
                    disabled={isSubmitting}
                  />
                </>
              )}
            />
          </div>
          {errors.color && (
            <p className="mt-1 text-sm text-red-600">{errors.color.message}</p>
          )}
        </div>

        {showStatusToggle && (
          <div className="flex items-center justify-between rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
            <div>
              <p className="text-sm font-medium text-gray-700">Tag ativa</p>
              <p className="text-xs text-gray-500">
                Tags inativas não ficam disponíveis no cadastro de agendamentos.
              </p>
            </div>
            <label className="inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                {...register('is_active')}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                disabled={isSubmitting}
              />
              <span className="ml-2 text-sm text-gray-700">
                {initialData?.is_active ? 'Ativa' : 'Inativa'}
              </span>
            </label>
          </div>
        )}

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={isSubmitting}
          >
            {initialData ? 'Salvar alterações' : 'Criar tag'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
