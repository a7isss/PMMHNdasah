// 🎯 Professional Select Component - Inspired by Plane's dropdown patterns
// Advanced select with search, multi-select, and accessibility

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '../../lib/utils';

export type SelectVariant = 'default' | 'error' | 'success';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  description?: string;
}

export interface SelectProps {
  /** Select options */
  options: SelectOption[];
  /** Selected value(s) */
  value?: string | number | (string | number)[] | null;
  /** Multiple selection mode */
  multiple?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Label text */
  label?: string;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Full width */
  fullWidth?: boolean;
  /** Required field indicator */
  required?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Searchable */
  searchable?: boolean;
  /** Allow clearing selection */
  clearable?: boolean;
  /** Maximum selections for multiple mode */
  maxSelections?: number;
  /** Custom className */
  className?: string;
  /** Change handler */
  onChange?: (value: string | number | (string | number)[] | null) => void;
  /** Search change handler */
  onSearchChange?: (search: string) => void;
}

export const Select = React.forwardRef<HTMLDivElement, SelectProps>(({
  options,
  value,
  multiple = false,
  placeholder = 'Select...',
  label,
  error,
  helperText,
  fullWidth = false,
  required = false,
  disabled = false,
  searchable = false,
  clearable = true,
  maxSelections,
  className,
  onChange,
  onSearchChange,
  ...props
}, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Generate unique ID
  const selectId = `select-${Math.random().toString(36).substr(2, 9)}`;

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchable && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [isOpen, searchable]);

  // Filter options based on search
  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (option.description && option.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Get selected options
  const getSelectedOptions = () => {
    if (!value) return [];

    if (multiple) {
      const values = Array.isArray(value) ? value : [value];
      return options.filter(option => values.includes(option.value));
    } else {
      return options.filter(option => option.value === value);
    }
  };

  const selectedOptions = getSelectedOptions();

  // Handle option selection
  const handleOptionSelect = (option: SelectOption) => {
    if (option.disabled) return;

    if (multiple) {
      const currentValues = Array.isArray(value) ? value : (value ? [value] : []);
      const isSelected = currentValues.includes(option.value);

      let newValues: (string | number)[];
      if (isSelected) {
        newValues = currentValues.filter(v => v !== option.value);
      } else {
        if (maxSelections && currentValues.length >= maxSelections) {
          return; // Don't allow more selections
        }
        newValues = [...currentValues, option.value];
      }

      onChange?.(newValues.length > 0 ? newValues : null);
    } else {
      onChange?.(option.value);
      setIsOpen(false);
      setSearchQuery('');
    }
  };

  // Handle clear selection
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(null);
    setSearchQuery('');
  };

  // Handle search change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearchChange?.(query);
  };

  // Check if option is selected
  const isOptionSelected = (optionValue: string | number) => {
    if (multiple) {
      return Array.isArray(value) && value.includes(optionValue);
    }
    return value === optionValue;
  };

  return (
    <div className={cn('flex flex-col', fullWidth && 'w-full')} ref={ref}>
      {/* Label */}
      {label && (
        <label
          htmlFor={selectId}
          className={cn(
            'block text-sm font-medium mb-1',
            error ? 'text-red-700' : 'text-gray-700'
          )}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Select Container */}
      <div className="relative" ref={containerRef}>
        {/* Trigger Button */}
        <button
          id={selectId}
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={cn(
            'w-full flex items-center justify-between',
            'px-3 py-2 text-left border rounded-md shadow-sm',
            'bg-white transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            disabled && 'opacity-50 cursor-not-allowed bg-gray-50',
            error ? 'border-red-300' : 'border-gray-300',
            fullWidth && 'w-full',
            className
          )}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-labelledby={label ? `${selectId}-label` : undefined}
        >
          {/* Selected Values Display */}
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {selectedOptions.length > 0 ? (
              multiple ? (
                <div className="flex items-center gap-1 flex-wrap">
                  {selectedOptions.slice(0, 2).map(option => (
                    <span
                      key={option.value}
                      className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-md"
                    >
                      {option.icon}
                      <span className="truncate">{option.label}</span>
                      <span
                        className="cursor-pointer hover:text-blue-600 text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOptionSelect(option);
                        }}
                      >
                        ×
                      </span>
                    </span>
                  ))}
                  {selectedOptions.length > 2 && (
                    <span className="text-xs text-gray-500">
                      +{selectedOptions.length - 2} more
                    </span>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  {selectedOptions[0].icon}
                  <span className="truncate">{selectedOptions[0].label}</span>
                </div>
              )
            ) : (
              <span className="text-gray-500 truncate">{placeholder}</span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1">
            {clearable && selectedOptions.length > 0 && (
              <span
                className="text-gray-400 hover:text-gray-600 cursor-pointer text-lg leading-none"
                onClick={handleClear}
              >
                ×
              </span>
            )}
            <span
              className={cn(
                'text-gray-400 transition-transform duration-200 text-xs',
                isOpen && 'transform rotate-180'
              )}
            >
              ▼
            </span>
          </div>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-hidden">
            {/* Search Input */}
            {searchable && (
              <div className="p-2 border-b border-gray-200">
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 text-sm">🔍</span>
                  <input
                    ref={searchInputRef}
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className="w-full pl-10 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
            )}

            {/* Options List */}
            <div className="max-h-48 overflow-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map(option => {
                  const isSelected = isOptionSelected(option.value);
                  const isDisabled = option.disabled ||
                    (multiple && maxSelections && Array.isArray(value) && value.length >= maxSelections && !isSelected);

                  return (
                    <div
                      key={option.value}
                      onClick={() => !isDisabled && handleOptionSelect(option)}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 cursor-pointer transition-colors',
                        isSelected && 'bg-blue-50 text-blue-700',
                        !isSelected && 'hover:bg-gray-50',
                        isDisabled && 'opacity-50 cursor-not-allowed'
                      )}
                      role="option"
                      aria-selected={isSelected}
                    >
                      {/* Selection Indicator */}
                      {multiple && (
                        <div className={cn(
                          'w-4 h-4 border rounded flex items-center justify-center',
                          isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-300'
                        )}>
                        {isSelected && <span className="text-white text-xs">✓</span>}
                        </div>
                      )}

                      {/* Option Content */}
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {option.icon}
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{option.label}</div>
                          {option.description && (
                            <div className="text-xs text-gray-500 truncate">{option.description}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="px-3 py-4 text-center text-gray-500 text-sm">
                  No options found
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Helper text or error message */}
      {(helperText || error) && (
        <p className={cn(
          'mt-1 text-sm',
          error ? 'text-red-600' : 'text-gray-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

export default Select;
