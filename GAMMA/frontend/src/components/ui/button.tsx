// 🎯 Professional Button Component - Inspired by Plane's component patterns
// Comprehensive button with variants, sizes, states, and accessibility features

import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';
import { variants } from '../../lib/utils';

// Button variant types
export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'neutral' | 'link';
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

// Button props interface
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button style variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Loading state */
  loading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
  /** Icon before text */
  prependIcon?: LucideIcon;
  /** Icon after text */
  appendIcon?: LucideIcon;
  /** Children content */
  children: React.ReactNode;
}

// Loading spinner component
const Spinner = ({ size = 'sm' }: { size?: 'xs' | 'sm' | 'md' }) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
  };

  return (
    <svg
      className={cn('animate-spin', sizeClasses[size])}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// Main Button component
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  prependIcon: PrependIcon,
  appendIcon: AppendIcon,
  className,
  children,
  ...props
}, ref) => {
  // Base button classes (Plane-inspired)
  const baseClasses = cn(
    // Base styles
    'inline-flex items-center justify-center',
    'font-medium transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    // Loading state
    loading && 'cursor-wait',
    // Full width
    fullWidth && 'w-full',
    // Custom className
    className
  );

  // Variant classes (Plane-inspired color system)
  const variantClasses = {
    primary: cn(
      'bg-blue-600 text-white',
      'hover:bg-blue-700',
      'focus:ring-blue-500',
      'active:bg-blue-800'
    ),
    secondary: cn(
      'bg-gray-200 text-gray-900',
      'hover:bg-gray-300',
      'focus:ring-gray-500',
      'active:bg-gray-400'
    ),
    danger: cn(
      'bg-red-600 text-white',
      'hover:bg-red-700',
      'focus:ring-red-500',
      'active:bg-red-800'
    ),
    neutral: cn(
      'bg-white text-gray-700 border border-gray-300',
      'hover:bg-gray-50',
      'focus:ring-gray-500',
      'active:bg-gray-100'
    ),
    link: cn(
      'text-blue-600 underline-offset-4',
      'hover:text-blue-800 hover:underline',
      'focus:ring-blue-500',
      'active:text-blue-900'
    ),
  };

  // Size classes (Plane-inspired sizing)
  const sizeClasses = {
    xs: 'h-6 px-2 text-xs rounded gap-1',
    sm: 'h-8 px-3 text-sm rounded-md gap-1.5',
    md: 'h-10 px-4 text-sm rounded-md gap-2',
    lg: 'h-12 px-6 text-base rounded-md gap-2',
    xl: 'h-14 px-8 text-lg rounded-lg gap-3',
  };

  // Icon size mapping
  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
    xl: 'w-6 h-6',
  };

  return (
    <button
      ref={ref}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size]
      )}
      disabled={disabled || loading}
      {...props}
    >
      {/* Loading spinner */}
      {loading && (
        <Spinner size={size === 'xs' ? 'xs' : 'sm'} />
      )}

      {/* Prepend icon */}
      {PrependIcon && !loading && (
        <PrependIcon className={iconSizes[size]} />
      )}

      {/* Button content */}
      {children}

      {/* Append icon */}
      {AppendIcon && (
        <AppendIcon className={iconSizes[size]} />
      )}
    </button>
  );
});

Button.displayName = 'Button';

// Export types for external use
export type { ButtonProps };
export { Button, Spinner };
export default Button;
