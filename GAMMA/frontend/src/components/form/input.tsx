// 🎯 Professional Input Component - Inspired by Plane's form patterns
// Comprehensive input with validation states, icons, and accessibility

import React, { useState } from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

// Input variant types
export type InputVariant = 'default' | 'error' | 'success';
export type InputSize = 'sm' | 'md' | 'lg';

// Input props interface
export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input style variant */
  variant?: InputVariant;
  /** Input size */
  size?: InputSize;
  /** Left icon */
  leftIcon?: LucideIcon;
  /** Right icon */
  rightIcon?: LucideIcon;
  /** Error message */
  error?: string;
  /** Helper text */
  helperText?: string;
  /** Full width */
  fullWidth?: boolean;
  /** Label text */
  label?: string;
  /** Required field indicator */
  required?: boolean;
}

// Input component
const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  variant = 'default',
  size = 'md',
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  error,
  helperText,
  fullWidth = false,
  label,
  required = false,
  className,
  id,
  ...props
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);

  // Generate unique ID if not provided
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  // Base input classes
  const baseClasses = cn(
    'w-full border rounded-md shadow-sm transition-all duration-200',
    'focus:outline-none focus:ring-2',
    'placeholder:text-gray-400',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    // Full width
    fullWidth && 'w-full',
    // Custom className
    className
  );

  // Size classes
  const sizeClasses = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-3 text-sm',
    lg: 'h-12 px-4 text-base',
  };

  // Variant classes
  const variantClasses = {
    default: cn(
      'border-gray-300',
      'focus:border-blue-500 focus:ring-blue-500/20',
      isFocused && 'border-blue-500 ring-2 ring-blue-500/20'
    ),
    error: cn(
      'border-red-300',
      'focus:border-red-500 focus:ring-red-500/20',
      isFocused && 'border-red-500 ring-2 ring-red-500/20'
    ),
    success: cn(
      'border-green-300',
      'focus:border-green-500 focus:ring-green-500/20',
      isFocused && 'border-green-500 ring-2 ring-green-500/20'
    ),
  };

  // Icon size mapping
  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  // Icon container classes
  const iconContainerClasses = {
    sm: 'px-2',
    md: 'px-3',
    lg: 'px-3',
  };

  return (
    <div className={cn('flex flex-col', fullWidth && 'w-full')}>
      {/* Label */}
      {label && (
        <label
          htmlFor={inputId}
          className={cn(
            'block text-sm font-medium mb-1',
            error ? 'text-red-700' : 'text-gray-700'
          )}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input container */}
      <div className="relative">
        {/* Left icon */}
        {LeftIcon && (
          <div className={cn(
            'absolute inset-y-0 left-0 flex items-center pointer-events-none',
            iconContainerClasses[size]
          )}>
            <LeftIcon className={cn('text-gray-400', iconSizes[size])} />
          </div>
        )}

        {/* Input element */}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            baseClasses,
            sizeClasses[size],
            variantClasses[variant],
            LeftIcon && 'pl-10',
            RightIcon && 'pr-10'
          )}
          onFocus={(e) => {
            setIsFocused(true);
            props.onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            props.onBlur?.(e);
          }}
          {...props}
        />

        {/* Right icon */}
        {RightIcon && (
          <div className={cn(
            'absolute inset-y-0 right-0 flex items-center pointer-events-none',
            iconContainerClasses[size]
          )}>
            <RightIcon className={cn('text-gray-400', iconSizes[size])} />
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

Input.displayName = 'Input';

// Export types
export type { InputProps };
export { Input };
export default Input;
