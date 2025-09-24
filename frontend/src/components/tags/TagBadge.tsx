import { XMarkIcon } from '@heroicons/react/20/solid';
import React from 'react';
import { getReadableTextColor, withAlpha } from '../../utils/color';

interface TagBadgeProps {
  name: string;
  color: string;
  onRemove?: () => void;
  className?: string;
  size?: 'sm' | 'md';
}

export const TagBadge: React.FC<TagBadgeProps> = ({
  name,
  color,
  onRemove,
  className = '',
  size = 'md',
}) => {
  const backgroundColor = withAlpha(color, 0.18);
  const textColor = getReadableTextColor(color);
  const paddingClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-medium transition-colors ${paddingClasses} ${className}`}
      style={{
        backgroundColor,
        borderColor: withAlpha(color, 0.6),
        color: textColor,
      }}
    >
      <span className="flex items-center gap-1">
        <span
          className="inline-block h-2.5 w-2.5 rounded-full border border-white/40"
          style={{ backgroundColor: color }}
          aria-hidden
        />
        {name}
      </span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-white/30 text-current transition hover:bg-white/50 focus:outline-none"
          aria-label={`Remover tag ${name}`}
        >
          <XMarkIcon className="h-3 w-3" />
        </button>
      )}
    </span>
  );
};
