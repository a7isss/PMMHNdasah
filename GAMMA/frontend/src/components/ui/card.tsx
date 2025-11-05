// 🎯 Professional Card Component - Inspired by Plane's card patterns
// Flexible card component with header, content, footer sections and variants

import React from 'react';
import { cn } from '../../lib/utils';

// Card variant types
export type CardVariant = 'default' | 'elevated' | 'outlined';

// Card props interface
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Card style variant */
  variant?: CardVariant;
  /** Card padding size */
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** Hover effects */
  hover?: boolean;
  /** Card content */
  children: React.ReactNode;
}

// Card sub-components
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

// Main Card component
const Card = React.forwardRef<HTMLDivElement, CardProps>(({
  variant = 'default',
  padding = 'md',
  hover = false,
  className,
  children,
  ...props
}, ref) => {
  // Base card classes
  const baseClasses = cn(
    'rounded-lg border bg-white transition-all duration-200',
    // Hover effects
    hover && 'hover:shadow-md hover:-translate-y-0.5',
    // Custom className
    className
  );

  // Variant classes (Plane-inspired)
  const variantClasses = {
    default: 'border-gray-200 shadow-sm',
    elevated: 'border-gray-200 shadow-md',
    outlined: 'border-2 border-gray-300 shadow-none',
  };

  // Padding classes
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  };

  return (
    <div
      ref={ref}
      className={cn(
        baseClasses,
        variantClasses[variant],
        paddingClasses[padding]
      )}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';

// Card Header sub-component
const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(({
  className,
  children,
  ...props
}, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex flex-col space-y-1.5 pb-4',
      className
    )}
    {...props}
  >
    {children}
  </div>
));

CardHeader.displayName = 'CardHeader';

// Card Content sub-component
const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(({
  className,
  children,
  ...props
}, ref) => (
  <div
    ref={ref}
    className={cn(
      'pt-0',
      className
    )}
    {...props}
  >
    {children}
  </div>
));

CardContent.displayName = 'CardContent';

// Card Footer sub-component
const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(({
  className,
  children,
  ...props
}, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center pt-4',
      className
    )}
    {...props}
  >
    {children}
  </div>
));

CardFooter.displayName = 'CardFooter';

// Export all components
export { Card, CardHeader, CardContent, CardFooter };
export type { CardProps, CardHeaderProps, CardContentProps, CardFooterProps };
export default Card;
