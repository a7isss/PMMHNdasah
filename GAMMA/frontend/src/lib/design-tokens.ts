// 🎨 Design Tokens - Inspired by Plane's Professional Design System
// Comprehensive design system with consistent spacing, colors, and typography

export const designTokens = {
  // Color Palette - Professional and accessible
  colors: {
    // Primary Brand Colors
    primary: {
      50: '#eff6ff',   // Very light blue
      100: '#dbeafe',  // Light blue
      200: '#bfdbfe',  // Lighter blue
      300: '#93c5fd',  // Light medium blue
      400: '#60a5fa',  // Medium blue
      500: '#3b82f6',  // Primary blue (main brand color)
      600: '#2563eb',  // Darker blue
      700: '#1d4ed8',  // Dark blue
      800: '#1e40af',  // Very dark blue
      900: '#1e3a8a',  // Darkest blue
      950: '#172554',  // Ultra dark blue
    },

    // Secondary Colors
    secondary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },

    // Success Colors
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d',
    },

    // Warning Colors
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },

    // Danger/Error Colors
    danger: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },

    // Neutral Colors (Grays)
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },

    // Background Colors
    background: {
      50: '#ffffff',   // Pure white
      100: '#fafbfc',  // Very light gray
      200: '#f6f8fa',  // Light gray background
      300: '#f1f3f4',  // Medium light background
      400: '#e8eaed',  // Sidebar background
      500: '#dadce0',  // Border colors
      600: '#bdc1c6',  // Secondary borders
      700: '#9aa0a6',  // Muted text
      800: '#5f6368',  // Body text
      900: '#202124',  // Dark text
    },
  },

  // Spacing Scale - 4px increments (Plane-inspired)
  spacing: {
    0: '0px',
    0.5: '0.125rem',  // 2px
    1: '0.25rem',     // 4px
    1.5: '0.375rem',  // 6px
    2: '0.5rem',      // 8px
    2.5: '0.625rem',  // 10px
    3: '0.75rem',     // 12px
    3.5: '0.875rem',  // 14px
    4: '1rem',        // 16px
    5: '1.25rem',     // 20px
    6: '1.5rem',      // 24px
    7: '1.75rem',     // 28px
    8: '2rem',        // 32px
    9: '2.25rem',     // 36px
    10: '2.5rem',     // 40px
    11: '2.75rem',    // 44px
    12: '3rem',       // 48px
    14: '3.5rem',     // 56px
    16: '4rem',       // 64px
    18: '4.5rem',     // 72px
    20: '5rem',       // 80px
    24: '6rem',       // 96px
    28: '7rem',       // 112px
    32: '8rem',       // 128px
    36: '9rem',       // 144px
    40: '10rem',      // 160px
    44: '11rem',      // 176px
    48: '12rem',      // 192px
    52: '13rem',      // 208px
    56: '14rem',      // 224px
    60: '15rem',      // 240px
    64: '16rem',      // 256px
    72: '18rem',      // 288px
    80: '20rem',      // 320px
    96: '24rem',      // 384px
  },

  // Typography Scale
  typography: {
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
      sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
      base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
      lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
      xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
      '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
      '5xl': ['3rem', { lineHeight: '1' }],          // 48px
      '6xl': ['3.75rem', { lineHeight: '1' }],       // 60px
      '7xl': ['4.5rem', { lineHeight: '1' }],        // 72px
      '8xl': ['6rem', { lineHeight: '1' }],          // 96px
      '9xl': ['8rem', { lineHeight: '1' }],          // 128px
    },

    fontWeight: {
      thin: '100',
      extralight: '200',
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
      black: '900',
    },

    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0em',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },

  // Border Radius Scale
  borderRadius: {
    none: '0px',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px',   // Fully rounded
  },

  // Shadows - Professional depth system
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: '0 0 #0000',
  },

  // Z-Index Scale
  zIndex: {
    0: '0',
    10: '10',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    60: '60',
    70: '70',
    80: '80',
    90: '90',
    100: '100',
    auto: 'auto',
  },

  // Transitions
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Breakpoints (Tailwind defaults with custom additions)
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// Type exports for TypeScript
export type ColorPalette = typeof designTokens.colors;
export type SpacingScale = typeof designTokens.spacing;
export type TypographyScale = typeof designTokens.typography;
export type BorderRadiusScale = typeof designTokens.borderRadius;
export type ShadowScale = typeof designTokens.shadows;
export type ZIndexScale = typeof designTokens.zIndex;
export type TransitionScale = typeof designTokens.transitions;
export type BreakpointScale = typeof designTokens.breakpoints;

// Utility functions for design token access
export const getColor = (color: keyof ColorPalette, shade: string | number = 500) => {
  const colorGroup = designTokens.colors[color];
  return colorGroup?.[shade as keyof typeof colorGroup] || colorGroup?.[500];
};

export const getSpacing = (size: keyof SpacingScale) => designTokens.spacing[size];
export const getFontSize = (size: keyof TypographyScale['fontSize']) => designTokens.typography.fontSize[size];
export const getBorderRadius = (size: keyof BorderRadiusScale) => designTokens.borderRadius[size];
export const getShadow = (size: keyof ShadowScale) => designTokens.shadows[size];
export const getZIndex = (level: keyof ZIndexScale) => designTokens.zIndex[level];
