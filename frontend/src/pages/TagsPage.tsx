import {
  PencilSquareIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import React, { useEffect, useMemo, useState } from 'react';
import { TagFormModal, type TagFormValues } from '../components/tags/TagFormModal';
import { TagBadge } from '../components/tags/TagBadge';
import { ToastContainer } from '../components/ui/Toast';
import { useToast } from '../hooks/useToast';
import type { Tag, TagListResponse } from '../types/tag';
import { tagAPI } from '../services/api';
import { formatDateTimeLabel } from '../utils/dateUtils';

const PAGE_SIZE = 20;

export const TagsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { toasts, success: showToastSuccess, error: showToastError, removeToast } = useToast();

  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setSearch(searchInput.trim());
      setPage(1);
    }, 350);
    return () => window.clearTimeout(handle);
  }, [searchInput]);

  const tagsQuery = useQuery<TagListResponse>({
    queryKey: ['tags', { page, search, includeInactive }],
    queryFn: () =>
      tagAPI.listTags({
        page,
        page_size: PAGE_SIZE,
        search: search || undefined,
        include_inactive: includeInactive,
      }),
    placeholderData: keepPreviousData,
  });

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingTag(null);
  };

  const invalidateTags = () => {
    queryClient.invalidateQueries({ queryKey: ['tags'] });
    queryClient.invalidateQueries({ queryKey: ['activeTags'] });
  };

  const createTagMutation = useMutation({
    mutationFn: (values: TagFormValues) => tagAPI.createTag({
      name: values.name,
      color: values.color,
    }),
    onSuccess: () => {
      showToastSuccess('Tag criada com sucesso.');
      closeModal();
      invalidateTags();
    },
    onError: () => {
      showToastError('Não foi possível criar a tag.');
    },
  });

  const updateTagMutation = useMutation({
    mutationFn: ({ id, values }: { id: string; values: TagFormValues }) =>
      tagAPI.updateTag(id, values),
    onSuccess: () => {
      showToastSuccess('Tag atualizada com sucesso.');
      closeModal();
      invalidateTags();
    },
    onError: () => {
      showToastError('Não foi possível atualizar a tag.');
    },
  });

  const deleteTagMutation = useMutation({
    mutationFn: (id: string) => tagAPI.deleteTag(id),
    onSuccess: (response) => {
      showToastSuccess(response.message || 'Tag removida com sucesso.');
      invalidateTags();
    },
    onError: (error: unknown) => {
      if (
        error &&
        typeof error === 'object' &&
        'response' in error &&
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      ) {
        showToastError((error as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Não foi possível remover a tag.');
        return;
      }
      showToastError('Não foi possível remover a tag.');
    },
  });

  const handleSubmit = async (values: TagFormValues) => {
    if (editingTag) {
      await updateTagMutation.mutateAsync({ id: editingTag.id, values });
      return;
    }
    await createTagMutation.mutateAsync(values);
  };

  const handleDelete = (tag: Tag) => {
    if (tag.is_active === false) {
      const confirmed = window.confirm(
        'Remover esta tag irá ocultá-la definitivamente. Deseja continuar?'
      );
      if (!confirmed) {
        return;
      }
    } else {
      const confirmed = window.confirm(
        'Esta tag pode estar associada a agendamentos. Tem certeza que deseja removê-la?'
      );
      if (!confirmed) {
        return;
      }
    }

    deleteTagMutation.mutate(tag.id);
  };

  const openCreateModal = () => {
    setEditingTag(null);
    setIsModalOpen(true);
  };

  const openEditModal = (tag: Tag) => {
    setEditingTag(tag);
    setIsModalOpen(true);
  };

  const isSubmitting =
    createTagMutation.isPending || updateTagMutation.isPending;

  const data = tagsQuery.data;
  const totalPages = data?.pages ?? 1;
  const totalItems = data?.total ?? 0;

  const tableRows = useMemo<Tag[]>(() => data?.data ?? [], [data]);

  return (
    <div className="space-y-6">
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Gestão de tags
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Crie, edite e organize as tags utilizadas nos agendamentos.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <PlusIcon className="h-4 w-4" />
          Nova tag
        </button>
      </div>

      <div className="flex flex-col gap-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:w-72">
            <input
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
              placeholder="Buscar por nome da tag"
            />
          </div>
          <label className="inline-flex items-center text-sm text-gray-600">
            <input
              type="checkbox"
              className="mr-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              checked={includeInactive}
              onChange={(event) => {
                setIncludeInactive(event.target.checked);
                setPage(1);
              }}
            />
            Incluir tags inativas
          </label>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Tag
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Criada em
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Atualizada em
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {tagsQuery.isLoading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-500">
                    Carregando tags...
                  </td>
                </tr>
              ) : tableRows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center text-sm text-gray-500">
                    Nenhuma tag encontrada.
                  </td>
                </tr>
              ) : (
                tableRows.map((tag) => (
                  <tr key={tag.id}>
                    <td className="px-4 py-3">
                      <div className="flex flex-col gap-1">
                        <TagBadge name={tag.name} color={tag.color} />
                        <span className="text-xs text-gray-400">{tag.id}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${
                          tag.is_active
                            ? 'bg-green-50 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {tag.is_active ? 'Ativa' : 'Inativa'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {formatDateTimeLabel(tag.created_at)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {tag.updated_at ? formatDateTimeLabel(tag.updated_at) : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => openEditModal(tag)}
                          className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                          <PencilSquareIcon className="h-4 w-4" />
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(tag)}
                          className="inline-flex items-center gap-1 rounded-md border border-red-200 px-3 py-1.5 text-sm text-red-600 transition hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        >
                          <TrashIcon className="h-4 w-4" />
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-3 border-t border-gray-200 pt-4 md:flex-row md:items-center md:justify-between">
          <p className="text-sm text-gray-500">
            {totalItems} tag{totalItems === 1 ? '' : 's'} encontradas
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page <= 1}
            >
              Anterior
            </button>
            <span className="text-sm text-gray-500">
              Página {page} de {totalPages}
            </span>
            <button
              type="button"
              className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
              disabled={page >= totalPages}
            >
              Próxima
            </button>
          </div>
        </div>
      </div>

      <TagFormModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        initialData={editingTag}
      />
    </div>
  );
};
