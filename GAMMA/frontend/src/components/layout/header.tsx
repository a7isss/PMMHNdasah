// 🎯 Workspace Header - Plane-inspired header with breadcrumbs and user menu
// Professional header component with navigation context and user actions

'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import {
  Bell,
  Search,
  User,
  Settings,
  LogOut,
  ChevronRight,
  Home,
} from 'lucide-react';
import { useWorkspace } from '../../lib/providers/workspace-provider';
import { Button } from '../ui/button';
import { Input } from '../form/input';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface WorkspaceHeaderProps {
  title?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  className?: string;
}

export function WorkspaceHeader({
  title,
  breadcrumbs = [],
  actions,
  className
}: WorkspaceHeaderProps) {
  const pathname = usePathname();
  const { user, logout, tenantId } = useWorkspace();

  // Generate breadcrumbs from pathname if not provided
  const generatedBreadcrumbs = React.useMemo(() => {
    if (breadcrumbs.length > 0) return breadcrumbs;

    const pathSegments = pathname.split('/').filter(Boolean);
    const crumbs: BreadcrumbItem[] = [
      { label: 'Dashboard', href: `/${tenantId}/dashboard` }
    ];

    // Skip tenantId segment and build breadcrumbs
    const relevantSegments = pathSegments.slice(1);

    relevantSegments.forEach((segment, index) => {
      const path = `/${tenantId}/${relevantSegments.slice(0, index + 1).join('/')}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');

      if (segment !== 'dashboard') {
        crumbs.push({ label, href: path });
      }
    });

    return crumbs;
  }, [pathname, tenantId, breadcrumbs]);

  const handleLogout = () => {
    logout();
  };

  return (
    <header className={`bg-white border-b border-gray-200 px-6 py-4 ${className || ''}`}>
      <div className="flex items-center justify-between">
        {/* Left Section - Breadcrumbs and Title */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-1 text-sm">
            <Home className="w-4 h-4 text-gray-400" />
            {generatedBreadcrumbs.map((crumb, index) => (
              <React.Fragment key={index}>
                <ChevronRight className="w-3 h-3 text-gray-400" />
                {crumb.href && index < generatedBreadcrumbs.length - 1 ? (
                  <a
                    href={crumb.href}
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {crumb.label}
                  </a>
                ) : (
                  <span className="text-gray-900 font-medium">{crumb.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>

          {/* Page Title */}
          {title && (
            <div className="flex items-center gap-3 ml-4">
              <h1 className="text-xl font-semibold text-gray-900 truncate">
                {title}
              </h1>
            </div>
          )}
        </div>

        {/* Center Section - Search */}
        <div className="flex-1 max-w-md mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Search projects, tasks..."
              className="pl-10"
              size="sm"
            />
          </div>
        </div>

        {/* Right Section - Actions and User Menu */}
        <div className="flex items-center gap-4">
          {/* Custom Actions */}
          {actions}

          {/* Notifications */}
          <Button
            variant="neutral"
            size="sm"
            className="relative p-2"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            {/* Notification badge - conditionally show */}
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>

          {/* User Menu */}
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-600">
                  {user?.firstName?.[0]}{user?.lastName?.[0]}
                </span>
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-gray-900">
                  {user?.firstName} {user?.lastName}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {user?.role?.replace('_', ' ')}
                </p>
              </div>
            </div>

            {/* User Dropdown Menu */}
            <div className="relative group">
              <Button
                variant="neutral"
                size="sm"
                className="p-1"
                aria-label="User menu"
              >
                <User className="w-4 h-4" />
              </Button>

              {/* Dropdown */}
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-1">
                  <a
                    href={`/${tenantId}/profile`}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <User className="w-4 h-4" />
                    Profile
                  </a>
                  <a
                    href={`/${tenantId}/settings`}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings className="w-4 h-4" />
                    Settings
                  </a>
                  <hr className="my-1" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
