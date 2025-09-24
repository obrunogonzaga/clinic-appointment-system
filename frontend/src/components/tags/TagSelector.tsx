import { MagnifyingGlassIcon } from '@heroicons/react/20/solid';
import React, { useMemo, useState } from 'react';
import type { Tag } from '../../types/tag';
import { TagBadge } from './TagBadge';

interface TagSelectorProps {
  availableTags: Tag[];
  selectedTagIds: string[];
  onChange: (nextValue: string[]) => void;
  disabled?: boolean;
  maxSelected?: number;
}

export const TagSelector: React.FC<TagSelectorProps> = ({
  availableTags,
  selectedTagIds,
  onChange,
  disabled = false,
  maxSelected = 5,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const selectedTags = useMemo(() => {
    const tagMap = new Map(availableTags.map((tag) => [tag.id, tag]));
    return selectedTagIds
      .map((id) => tagMap.get(id))
      .filter((tag): tag is Tag => Boolean(tag));
  }, [availableTags, selectedTagIds]);

  const filteredTags = useMemo(() => {
    const normalizedTerm = searchTerm.trim().toLowerCase();
    if (!normalizedTerm) {
      return availableTags;
    }
    return availableTags.filter((tag) =>
      tag.name.toLowerCase().includes(normalizedTerm)
    );
  }, [availableTags, searchTerm]);

  const hasReachedLimit =
    maxSelected > 0 && selectedTagIds.length >= maxSelected;

  const toggleSelection = (tagId: string) => {
    if (disabled) {
      return;
    }

    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId));
      return;
    }

    if (hasReachedLimit) {
      return;
    }

    onChange([...selectedTagIds, tagId]);
  };

  const clearSelection = () => {
    if (!disabled) {
      onChange([]);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {selectedTags.length > 0 ? (
          selectedTags.map((tag) => (
            <TagBadge
              key={tag.id}
              name={tag.name}
              color={tag.color}
              onRemove={disabled ? undefined : () => toggleSelection(tag.id)}
              size="sm"
            />
          ))
        ) : (
          <p className="text-sm text-gray-500">
            Nenhuma tag selecionada.
          </p>
        )}
      </div>

      <div className="relative">
        <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        <input
          type="search"
          className="w-full rounded-md border border-gray-200 bg-white py-2 pl-9 pr-3 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:bg-gray-100"
          placeholder="Buscar tags..."
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          disabled={disabled}
        />
        {selectedTagIds.length > 0 && (
          <button
            type="button"
            className="absolute right-2 top-2 text-xs text-blue-600 hover:text-blue-500 focus:outline-none"
            onClick={clearSelection}
            disabled={disabled}
          >
            Limpar
          </button>
        )}
      </div>

      <div className="max-h-48 overflow-y-auto rounded-md border border-gray-200 bg-white shadow-sm">
        {filteredTags.length === 0 ? (
          <p className="p-3 text-sm text-gray-500">Nenhuma tag encontrada.</p>
        ) : (
          <ul className="divide-y divide-gray-100 text-sm">
            {filteredTags.map((tag) => {
              const isSelected = selectedTagIds.includes(tag.id);
              const isDisabled =
                disabled || (!isSelected && hasReachedLimit);

              return (
                <li key={tag.id}>
                  <button
                    type="button"
                    onClick={() => toggleSelection(tag.id)}
                    disabled={isDisabled}
                    className={`
                      flex w-full items-center justify-between px-3 py-2 transition-colors
                      ${isSelected ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}
                      ${isDisabled && !isSelected ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    <span className="flex items-center gap-2">
                      <span
                        className="inline-block h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: tag.color }}
                        aria-hidden
                      />
                      {tag.name}
                    </span>
                    {isSelected && (
                      <span className="text-xs font-medium uppercase text-blue-600">
                        Selecionada
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {hasReachedLimit && (
        <p className="text-xs text-amber-600">
          Limite máximo de {maxSelected} tags por agendamento atingido.
        </p>
      )}
    </div>
  );
};
