// 🎯 Professional Radio Component - Inspired by Plane's form patterns
// Accessible radio button with custom styling and states

import React from 'react';
import { cn } from '../../lib/utils';

export interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Label text */
  label?: string;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Custom className */
  className?: string;
  /** Radio size */
  size?: 'sm' | 'md' | 'lg';
}

export interface RadioGroupProps {
  /** Radio options */
  options: Array<{
    value: string | number;
    label: string;
    disabled?: boolean;
    description?: string;
  }>;
  /** Selected value */
  value?: string | number;
  /** Name attribute for the radio group */
  name: string;
  /** Label for the group */
  label?: string;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Orientation */
  orientation?: 'vertical' | 'horizontal';
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state */
  disabled?: boolean;
  /** Change handler */
  onChange?: (value: string | number) => void;
  /** Custom className */
  className?: string;
}

export const Radio = React.forwardRef<HTMLInputElement, RadioProps>(({
  label,
  error,
  helperText,
  className,
  size = 'md',
  id,
  ...props
}, ref) => {
  // Generate unique ID if not provided
  const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

  // Size configurations
  const sizeClasses = {
    sm: {
      container: 'gap-2',
      radio: 'w-4 h-4',
      dot: 'w-2 h-2',
      label: 'text-sm',
    },
    md: {
      container: 'gap-3',
      radio: 'w-5 h-5',
      dot: 'w-3 h-3',
      label: 'text-sm',
    },
    lg: {
      container: 'gap-4',
      radio: 'w-6 h-6',
      dot: 'w-4 h-4',
      label: 'text-base',
    },
  };

  return (
    <div className="flex flex-col">
      {/* Radio and Label Container */}
      <div className={cn('flex items-start', sizeClasses[size].container)}>
        {/* Hidden Native Radio */}
        <input
          ref={ref}
          id={radioId}
          type="radio"
          className="sr-only"
          {...props}
        />

        {/* Custom Radio */}
        <div
          className={cn(
            'relative flex items-center justify-center rounded-full border-2 transition-all duration-200',
            'focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2',
            // Base styles
            'border-gray-300 bg-white hover:border-gray-400',
            // Checked state
            props.checked && 'border-blue-600',
            // Error state
            error && 'border-red-500',
            // Disabled state
            props.disabled && 'opacity-50 cursor-not-allowed',
            // Size
            sizeClasses[size].radio,
            className
          )}
          onClick={() => {
            if (!props.disabled) {
              // Trigger the hidden radio
              const radio = document.getElementById(radioId) as HTMLInputElement;
              if (radio) {
                radio.click();
              }
            }
          }}
        >
          {/* Radio dot */}
          {props.checked && (
            <div
              className={cn(
                'rounded-full bg-blue-600 transition-all duration-200',
                sizeClasses[size].dot
              )}
            />
          )}
        </div>

        {/* Label */}
        {label && (
          <label
            htmlFor={radioId}
            className={cn(
              'cursor-pointer select-none font-medium leading-tight',
              error ? 'text-red-700' : 'text-gray-900',
              sizeClasses[size].label,
              props.disabled && 'cursor-not-allowed opacity-50'
            )}
            onClick={() => {
              if (!props.disabled) {
                const radio = document.getElementById(radioId) as HTMLInputElement;
                if (radio) {
                  radio.click();
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

Radio.displayName = 'Radio';

// Radio Group Component
export const RadioGroup = React.forwardRef<HTMLDivElement, RadioGroupProps>(({
  options,
  value,
  name,
  label,
  error,
  helperText,
  orientation = 'vertical',
  size = 'md',
  disabled = false,
  onChange,
  className,
  ...props
}, ref) => {
  const handleChange = (optionValue: string | number) => {
    onChange?.(optionValue);
  };

  return (
    <div className={cn('flex flex-col', className)} ref={ref}>
      {/* Group Label */}
      {label && (
        <label className={cn(
          'block text-sm font-medium mb-3',
          error ? 'text-red-700' : 'text-gray-700'
        )}>
          {label}
        </label>
      )}

      {/* Radio Options */}
      <div className={cn(
        'flex',
        orientation === 'vertical' ? 'flex-col gap-3' : 'flex-wrap gap-6'
      )}>
        {options.map((option) => (
          <Radio
            key={option.value}
            id={`${name}-${option.value}`}
            name={name}
            value={option.value}
            checked={value === option.value}
            disabled={disabled || option.disabled}
            size={size}
            label={option.label}
            onChange={() => handleChange(option.value)}
            {...props}
          />
        ))}
      </div>

      {/* Helper text or error message */}
      {(helperText || error) && (
        <p className={cn(
          'mt-3 text-sm',
          error ? 'text-red-600' : 'text-gray-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

RadioGroup.displayName = 'RadioGroup';

// Export types
export type { RadioProps, RadioGroupProps };
export { Radio, RadioGroup };
export default Radio;
