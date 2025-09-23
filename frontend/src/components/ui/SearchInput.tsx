import { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
  inputClassName?: string;
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Buscar...',
  debounceMs = 300,
  className = '',
  inputClassName = '',
  onKeyDown,
}: SearchInputProps) {
  const [internalValue, setInternalValue] = useState(value);

  // Update internal value when external value changes
  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Debounce the onChange callback
  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(internalValue);
    }, debounceMs);

    return () => clearTimeout(timeout);
  }, [internalValue, onChange, debounceMs]);

  const handleClear = () => {
    setInternalValue('');
    onChange('');
  };

  return (
    <div className={`relative ${className}`}>
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 dark:text-slate-500" />
      </div>
      
      <input
        type="text"
        value={internalValue}
        onChange={(e) => setInternalValue(e.target.value)}
        placeholder={placeholder}
        onKeyDown={onKeyDown}
        className={`block w-full rounded-md border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 py-2 pl-10 pr-10 leading-5 placeholder-gray-500 dark:placeholder:text-slate-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-indigo-400 focus:border-blue-500 dark:focus:border-indigo-400 text-gray-900 dark:text-slate-100 ${inputClassName}`}
      />
      
      {internalValue && (
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          <button
            onClick={handleClear}
            className="text-gray-400 dark:text-slate-500 hover:text-gray-500 dark:hover:text-slate-300 focus:outline-none focus:text-gray-500"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
}
