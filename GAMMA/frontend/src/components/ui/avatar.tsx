// 🎯 Professional Avatar Component - Inspired by Plane's user display patterns
// Flexible avatar with fallback initials and image support

import React from 'react';
import { User } from 'lucide-react';
import { cn } from '../../lib/utils';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Avatar image source */
  src?: string;
  /** Fallback text (usually initials) */
  fallback?: string;
  /** Avatar size */
  size?: AvatarSize;
  /** Custom className */
  className?: string;
  /** Show online status indicator */
  showStatus?: boolean;
  /** Online status */
  isOnline?: boolean;
  /** Custom status color */
  statusColor?: string;
}

export const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(({
  src,
  fallback,
  size = 'md',
  showStatus = false,
  isOnline = false,
  statusColor,
  className,
  ...props
}, ref) => {
  // Size configurations
  const sizeClasses = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-xl',
    '2xl': 'w-20 h-20 text-2xl',
  };

  // Status indicator size
  const statusSizeClasses = {
    xs: 'w-2 h-2',
    sm: 'w-2.5 h-2.5',
    md: 'w-3 h-3',
    lg: 'w-3.5 h-3.5',
    xl: 'w-4 h-4',
    '2xl': 'w-5 h-5',
  };

  // Generate fallback initials
  const getFallbackText = () => {
    if (fallback) return fallback;

    // If no fallback provided, show user icon
    return null;
  };

  const fallbackText = getFallbackText();

  return (
    <div className="relative inline-block">
      <div
        ref={ref}
        className={cn(
          'relative flex items-center justify-center rounded-full bg-gray-200 text-gray-600 font-medium overflow-hidden',
          'ring-2 ring-white',
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {src ? (
          // Image avatar
          <img
            src={src}
            alt="Avatar"
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback to initials if image fails to load
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const parent = target.parentElement;
              if (parent && fallbackText) {
                parent.textContent = fallbackText;
              } else if (parent) {
                // Show user icon as last resort
                parent.innerHTML = '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>';
              }
            }}
          />
        ) : fallbackText ? (
          // Text fallback
          <span className="font-semibold text-gray-700">
            {fallbackText}
          </span>
        ) : (
          // Icon fallback
          <User className={cn(
            'text-gray-400',
            size === 'xs' && 'w-3 h-3',
            size === 'sm' && 'w-4 h-4',
            size === 'md' && 'w-4 h-4',
            size === 'lg' && 'w-5 h-5',
            size === 'xl' && 'w-6 h-6',
            size === '2xl' && 'w-8 h-8'
          )} />
        )}
      </div>

      {/* Status indicator */}
      {showStatus && (
        <div
          className={cn(
            'absolute -bottom-0.5 -right-0.5 rounded-full border-2 border-white',
            statusColor || (isOnline ? 'bg-green-500' : 'bg-gray-400'),
            statusSizeClasses[size]
          )}
          title={isOnline ? 'Online' : 'Offline'}
        />
      )}
    </div>
  );
});

Avatar.displayName = 'Avatar';

// Avatar Group Component
export interface AvatarGroupProps {
  /** Array of avatar props */
  avatars: Array<{
    src?: string;
    fallback?: string;
    showStatus?: boolean;
    isOnline?: boolean;
  }>;
  /** Maximum avatars to show */
  max?: number;
  /** Avatar size */
  size?: AvatarSize;
  /** Spacing between avatars */
  spacing?: 'tight' | 'normal' | 'loose';
  /** Total count (for overflow indicator) */
  total?: number;
}

export const AvatarGroup = ({
  avatars,
  max = 5,
  size = 'md',
  spacing = 'normal',
  total
}: AvatarGroupProps) => {
  const visibleAvatars = avatars.slice(0, max);
  const overflowCount = total || (avatars.length > max ? avatars.length - max : 0);

  const spacingClasses = {
    tight: '-space-x-1',
    normal: '-space-x-2',
    loose: '-space-x-3',
  };

  return (
    <div className={cn('flex items-center', spacingClasses[spacing])}>
      {visibleAvatars.map((avatar, index) => (
        <Avatar
          key={index}
          src={avatar.src}
          fallback={avatar.fallback}
          size={size}
          showStatus={avatar.showStatus}
          isOnline={avatar.isOnline}
          className="ring-2 ring-white"
        />
      ))}

      {/* Overflow indicator */}
      {overflowCount > 0 && (
        <div
          className={cn(
            'flex items-center justify-center rounded-full bg-gray-200 text-gray-600 font-medium border-2 border-white',
            size === 'xs' && 'w-6 h-6 text-xs',
            size === 'sm' && 'w-8 h-8 text-sm',
            size === 'md' && 'w-10 h-10 text-base',
            size === 'lg' && 'w-12 h-12 text-lg',
            size === 'xl' && 'w-16 h-16 text-xl',
            size === '2xl' && 'w-20 h-20 text-2xl'
          )}
        >
          +{overflowCount}
        </div>
      )}
    </div>
  );
};

// Export types
export type { AvatarProps, AvatarGroupProps };
export { Avatar, AvatarGroup };
export default Avatar;
