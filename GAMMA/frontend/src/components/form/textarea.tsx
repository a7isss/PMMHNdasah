// 🎯 Professional Textarea Component - Inspired by Plane's form patterns
// Auto-resizing textarea with validation states and accessibility

import React, { useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';

export type TextareaVariant = 'default' | 'error' | 'success';
export type TextareaSize = 'sm' | 'md' | 'lg';

export interface TextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'> {
  /** Textarea style variant */
  variant?: TextareaVariant;
  /** Textarea size */
  size?: TextareaSize;
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
  /** Auto-resize behavior */
  autoResize?: boolean;
  /** Minimum height (when autoResize is true) */
  minHeight?: number;
  /** Maximum height (when autoResize is true) */
  maxHeight?: number;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({
  variant = 'default',
  size = 'md',
  label,
  error,
  helperText,
  fullWidth = false,
  required = false,
  autoResize = true,
  minHeight = 80,
  maxHeight = 200,
  className,
  id,
  style,
  ...props
}, ref) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const combinedRef = ref || textareaRef;

  // Generate unique ID if not provided
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  // Auto-resize functionality
  useEffect(() => {
    if (autoResize && combinedRef && 'current' in combinedRef && combinedRef.current) {
      const textarea = combinedRef.current;

      const adjustHeight = () => {
        textarea.style.height = 'auto';
        const scrollHeight = textarea.scrollHeight;
        const newHeight = Math.min(Math.max(scrollHeight, minHeight), maxHeight);
        textarea.style.height = `${newHeight}px`;
      };

      // Initial adjustment
      adjustHeight();

      // Adjust on value changes
      textarea.addEventListener('input', adjustHeight);

      return () => {
        textarea.removeEventListener('input', adjustHeight);
      };
    }
  }, [autoResize, minHeight, maxHeight, combinedRef]);

  // Base textarea classes
  const baseClasses = cn(
    'w-full border rounded-md shadow-sm transition-all duration-200',
    'focus:outline-none focus:ring-2',
    'placeholder:text-gray-400',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'resize-none', // Disable manual resize when autoResize is enabled
    // Full width
    fullWidth && 'w-full',
    // Custom className
    className
  );

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm min-h-[60px]',
    md: 'px-3 py-2 text-sm min-h-[80px]',
    lg: 'px-4 py-3 text-base min-h-[100px]',
  };

  // Variant classes
  const variantClasses = {
    default: cn(
      'border-gray-300',
      'focus:border-blue-500 focus:ring-blue-500/20'
    ),
    error: cn(
      'border-red-300',
      'focus:border-red-500 focus:ring-red-500/20'
    ),
    success: cn(
      'border-green-300',
      'focus:border-green-500 focus:ring-green-500/20'
    ),
  };

  return (
    <div className={cn('flex flex-col', fullWidth && 'w-full')}>
      {/* Label */}
      {label && (
        <label
          htmlFor={textareaId}
          className={cn(
            'block text-sm font-medium mb-1',
            error ? 'text-red-700' : 'text-gray-700'
          )}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Textarea */}
      <textarea
        ref={combinedRef}
        id={textareaId}
        className={cn(
          baseClasses,
          sizeClasses[size],
          variantClasses[variant]
        )}
        style={{
          ...style,
          ...(autoResize && { minHeight: `${minHeight}px`, maxHeight: `${maxHeight}px` }),
        }}
        {...props}
      />

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

Textarea.displayName = 'Textarea';

export default Textarea;
