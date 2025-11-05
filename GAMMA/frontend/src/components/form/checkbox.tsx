// 🎯 Professional Checkbox Component - Inspired by Plane's form patterns
// Accessible checkbox with custom styling and states

import React from 'react';
import { Check } from '@mui/icons-material';
import { cn } from '../../lib/utils';

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Label text */
  label?: string;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Custom className */
  className?: string;
  /** Checkbox size */
  size?: 'sm' | 'md' | 'lg';
  /** Indeterminate state */
  indeterminate?: boolean;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({
  label,
  error,
  helperText,
  className,
  size = 'md',
  indeterminate = false,
  id,
  ...props
}, ref) => {
  // Generate unique ID if not provided
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  // Size configurations
  const sizeClasses = {
    sm: {
      container: 'gap-2',
      checkbox: 'w-4 h-4',
      icon: 'w-3 h-3',
      label: 'text-sm',
    },
    md: {
      container: 'gap-3',
      checkbox: 'w-5 h-5',
      icon: 'w-4 h-4',
      label: 'text-sm',
    },
    lg: {
      container: 'gap-4',
      checkbox: 'w-6 h-6',
      icon: 'w-5 h-5',
      label: 'text-base',
    },
  };

  return (
    <div className="flex flex-col">
      {/* Checkbox and Label Container */}
      <div className={cn('flex items-start', sizeClasses[size].container)}>
        {/* Hidden Native Checkbox */}
        <input
          ref={ref}
          id={checkboxId}
          type="checkbox"
          className="sr-only"
          {...props}
        />

        {/* Custom Checkbox */}
        <div
          className={cn(
            'relative flex items-center justify-center rounded border-2 transition-all duration-200',
            'focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2',
            // Base styles
            'border-gray-300 bg-white hover:border-gray-400',
            // Checked state
            props.checked && 'border-blue-600 bg-blue-600',
            // Indeterminate state
            indeterminate && 'border-blue-600 bg-blue-600',
            // Error state
            error && 'border-red-500',
            // Disabled state
            props.disabled && 'opacity-50 cursor-not-allowed',
            // Size
            sizeClasses[size].checkbox,
            className
          )}
          onClick={() => {
            if (!props.disabled) {
              // Trigger the hidden checkbox
              const checkbox = document.getElementById(checkboxId) as HTMLInputElement;
              if (checkbox) {
                checkbox.click();
              }
            }
          }}
        >
          {/* Check Icon */}
          {(props.checked || indeterminate) && (
            <Check
              className={cn(
                'text-white transition-all duration-200',
                sizeClasses[size].icon
              )}
            />
          )}

          {/* Indeterminate dash */}
          {indeterminate && !props.checked && (
            <div className="w-3 h-0.5 bg-white rounded-full" />
          )}
        </div>

        {/* Label */}
        {label && (
          <label
            htmlFor={checkboxId}
            className={cn(
              'cursor-pointer select-none font-medium leading-tight',
              error ? 'text-red-700' : 'text-gray-900',
              sizeClasses[size].label,
              props.disabled && 'cursor-not-allowed opacity-50'
            )}
            onClick={() => {
              if (!props.disabled) {
                const checkbox = document.getElementById(checkboxId) as HTMLInputElement;
                if (checkbox) {
                  checkbox.click();
                }
              }
            }}
          >
            {label}
          </label>
        )}
      </div>

      {/* Helper text or error message */}
      {(helperText || error) && (
        <p className={cn(
          'mt-1 text-sm ml-8',
          error ? 'text-red-600' : 'text-gray-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

export default Checkbox;
