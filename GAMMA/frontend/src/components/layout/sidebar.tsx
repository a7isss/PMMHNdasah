// 🎯 Workspace Sidebar - Plane-inspired collapsible navigation
// Professional sidebar with project management navigation

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  BarChart3,
  Users,
  Settings,
  FileText,
  Building,
  Menu,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useWorkspace } from '../../lib/providers/workspace-provider';
import { Button } from '../ui/button';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  permission?: string;
  children?: NavigationItem[];
}

const navigationItems: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderKanban,
    permission: 'view_projects',
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: CheckSquare,
    permission: 'view_projects',
  },
  {
    name: 'Procurement',
    href: '/procurement',
    icon: Building,
    permission: 'view_projects',
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: BarChart3,
    permission: 'view_reports',
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users,
    permission: 'manage_users',
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: FileText,
    permission: 'view_projects',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    permission: 'manage_users',
  },
];

interface WorkspaceSidebarProps {
  className?: string;
}

export function WorkspaceSidebar({ className }: WorkspaceSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, hasPermission, tenantId } = useWorkspace();

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const isActiveRoute = (href: string) => {
    return pathname === `/${tenantId}${href}` || pathname.startsWith(`/${tenantId}${href}/`);
  };

  const filteredNavigation = navigationItems.filter(item =>
    !item.permission || hasPermission(item.permission)
  );

  return (
    <div className={cn(
      'flex flex-col bg-white border-r border-gray-200 transition-all duration-300',
      isCollapsed ? 'w-16' : 'w-64',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">G</span>
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">GAMMA</h2>
              <p className="text-xs text-gray-500">PM System</p>
            </div>
          </div>
        )}

        <Button
          variant="neutral"
          size="xs"
          onClick={toggleSidebar}
          className="p-1 h-6 w-6"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="w-3 h-3" />
          ) : (
            <ChevronLeft className="w-3 h-3" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {filteredNavigation.map((item) => {
          const Icon = item.icon;
          const isActive = isActiveRoute(item.href);
          const href = `/${tenantId}${item.href}`;

          return (
            <Link
              key={item.name}
              href={href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                'hover:bg-gray-100',
                isActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-700 hover:text-gray-900',
                isCollapsed && 'justify-center px-2'
              )}
            >
              <Icon className={cn(
                'flex-shrink-0',
                isCollapsed ? 'w-5 h-5' : 'w-4 h-4'
              )} />

              {!isCollapsed && (
                <span className="truncate">{item.name}</span>
              )}

              {isCollapsed && (
                <div className="absolute left-16 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      {!isCollapsed && user && (
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-600">
                {user.firstName?.[0]}{user.lastName?.[0]}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user.firstName} {user.lastName}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {user.role.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
