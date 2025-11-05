// 🎨 Utility Functions - Professional helper functions for consistent styling
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { designTokens, getColor, getSpacing, getBorderRadius, getShadow } from './design-tokens';

// Class name utility (combines clsx and tailwind-merge for optimal performance)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Design token utilities with fallbacks
export const colors = {
  primary: (shade: number = 500) => getColor('primary', shade) || designTokens.colors.primary[500],
  secondary: (shade: number = 500) => getColor('secondary', shade) || designTokens.colors.secondary[500],
  success: (shade: number = 500) => getColor('success', shade) || designTokens.colors.success[500],
  warning: (shade: number = 500) => getColor('warning', shade) || designTokens.colors.warning[500],
  danger: (shade: number = 500) => getColor('danger', shade) || designTokens.colors.danger[500],
  neutral: (shade: number = 500) => getColor('neutral', shade) || designTokens.colors.neutral[500],
  background: (shade: number = 50) => getColor('background', shade) || designTokens.colors.background[50],
};

export const spacing = {
  get: (size: keyof typeof designTokens.spacing) => getSpacing(size),
  px: (size: number) => `${size}px`,
  rem: (size: number) => `${size / 16}rem`,
};

export const typography = {
  fontSize: (size: keyof typeof designTokens.typography.fontSize) =>
    designTokens.typography.fontSize[size],
  fontWeight: (weight: keyof typeof designTokens.typography.fontWeight) =>
    designTokens.typography.fontWeight[weight],
  letterSpacing: (spacing: keyof typeof designTokens.typography.letterSpacing) =>
    designTokens.typography.letterSpacing[spacing],
};

export const borders = {
  radius: (size: keyof typeof designTokens.borderRadius) => getBorderRadius(size),
  width: {
    thin: '1px',
    base: '2px',
    thick: '3px',
  },
};

export const shadows = {
  get: (size: keyof typeof designTokens.shadows) => getShadow(size),
};

// Component variant utilities
export const variants = {
  button: {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    neutral: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-gray-500',
    link: 'text-blue-600 hover:text-blue-800 underline-offset-4 hover:underline focus:ring-blue-500',
  },

  buttonSize: {
    xs: 'h-6 px-2 text-xs rounded',
    sm: 'h-8 px-3 text-sm rounded-md',
    md: 'h-10 px-4 text-sm rounded-md',
    lg: 'h-12 px-6 text-base rounded-md',
    xl: 'h-14 px-8 text-lg rounded-lg',
  },

  input: {
    base: 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    error: 'border-red-300 focus:ring-red-500 focus:border-red-500',
    success: 'border-green-300 focus:ring-green-500 focus:border-green-500',
  },

  card: {
    default: 'bg-white border border-gray-200 rounded-lg shadow-sm',
    elevated: 'bg-white border border-gray-200 rounded-lg shadow-md',
    outlined: 'bg-white border-2 border-gray-200 rounded-lg',
  },
};

// Focus and interaction utilities
export const focusRing = 'focus:outline-none focus:ring-2 focus:ring-offset-2';
export const focusRingColors = {
  primary: 'focus:ring-blue-500',
  secondary: 'focus:ring-gray-500',
  danger: 'focus:ring-red-500',
  success: 'focus:ring-green-500',
};

// State utilities
export const states = {
  disabled: 'opacity-50 cursor-not-allowed pointer-events-none',
  loading: 'cursor-wait',
  hover: 'hover:bg-gray-50 transition-colors',
  active: 'active:bg-gray-100',
};

// Layout utilities
export const layout = {
  flex: {
    center: 'flex items-center justify-center',
    between: 'flex items-center justify-between',
    start: 'flex items-center justify-start',
    end: 'flex items-center justify-end',
    column: 'flex flex-col',
    columnCenter: 'flex flex-col items-center justify-center',
  },
  grid: {
    cols1: 'grid grid-cols-1',
    cols2: 'grid grid-cols-2',
    cols3: 'grid grid-cols-3',
    cols4: 'grid grid-cols-4',
    autoFit: 'grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))]',
    autoFill: 'grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))]',
  },
  spacing: {
    gap2: 'gap-2',
    gap4: 'gap-4',
    gap6: 'gap-6',
    gap8: 'gap-8',
  },
};

// Text utilities
export const text = {
  truncate: 'truncate',
  ellipsis: 'text-ellipsis overflow-hidden',
  clamp: (lines: number) => `line-clamp-${lines}`,
  colors: {
    primary: 'text-gray-900',
    secondary: 'text-gray-600',
    muted: 'text-gray-500',
    danger: 'text-red-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
  },
  sizes: {
    xs: 'text-xs',
    sm: 'text-sm',
    base: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
    '2xl': 'text-2xl',
    '3xl': 'text-3xl',
  },
};

// Animation utilities
export const animations = {
  spin: 'animate-spin',
  pulse: 'animate-pulse',
  bounce: 'animate-bounce',
  transition: 'transition-all duration-200 ease-in-out',
  scale: 'transform hover:scale-105 transition-transform',
};

// Responsive utilities
export const responsive = {
  hidden: {
    sm: 'hidden sm:block',
    md: 'hidden md:block',
    lg: 'hidden lg:block',
    xl: 'hidden xl:block',
  },
  flex: {
    sm: 'flex sm:hidden',
    md: 'flex md:hidden',
    lg: 'flex lg:hidden',
    xl: 'flex xl:hidden',
  },
};

// Accessibility utilities
export const a11y = {
  srOnly: 'sr-only',
  focusVisible: 'focus-visible',
  screenReader: 'sr-only',
  skipLink: 'absolute -top-full left-6 z-50 bg-blue-600 text-white px-4 py-2 rounded-md focus:top-6 transition-all',
};

// Form utilities
export const forms = {
  label: 'block text-sm font-medium text-gray-700 mb-1',
  error: 'mt-1 text-sm text-red-600',
  help: 'mt-1 text-sm text-gray-500',
  required: 'after:content-["*"] after:text-red-500 after:ml-1',
};

// Data display utilities
export const dataDisplay = {
  badge: {
    base: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
    variants: {
      primary: 'bg-blue-100 text-blue-800',
      secondary: 'bg-gray-100 text-gray-800',
      success: 'bg-green-100 text-green-800',
      danger: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
    },
  },
  avatar: {
    base: 'inline-flex items-center justify-center rounded-full',
    sizes: {
      xs: 'w-6 h-6 text-xs',
      sm: 'w-8 h-8 text-sm',
      md: 'w-10 h-10 text-base',
      lg: 'w-12 h-12 text-lg',
      xl: 'w-16 h-16 text-xl',
    },
  },
};

// Export all utilities
export {
  designTokens,
  colors as colorUtils,
  spacing as spacingUtils,
  typography as typographyUtils,
  borders as borderUtils,
  shadows as shadowUtils,
};
