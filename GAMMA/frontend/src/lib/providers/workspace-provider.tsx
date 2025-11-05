// 🎯 Workspace Provider - Plane-inspired context management
// Manages workspace state, user permissions, and tenant context

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'user' | 'admin' | 'super_admin';
  tenantId: string;
}

interface WorkspaceContextType {
  tenantId: string;
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  hasPermission: (permission: string) => boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

interface WorkspaceProviderProps {
  tenantId: string;
  children: React.ReactNode;
}

export function WorkspaceProvider({ tenantId, children }: WorkspaceProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check authentication and load user data
  useEffect(() => {
    checkAuthStatus();
  }, [tenantId]);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setIsLoading(false);
        return;
      }

      // Verify token and get user info
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token invalid, redirect to login
        localStorage.removeItem('access_token');
        router.push('/login');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('access_token');
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    await checkAuthStatus();
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    router.push('/login');
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;

    // Super admin has all permissions
    if (user.role === 'super_admin') return true;

    // Admin permissions
    if (user.role === 'admin') {
      const adminPermissions = [
        'create_project',
        'edit_project',
        'delete_project',
        'manage_users',
        'view_reports',
      ];
      return adminPermissions.includes(permission);
    }

    // Regular user permissions
    const userPermissions = [
      'view_projects',
      'create_task',
      'edit_own_tasks',
      'view_reports',
    ];
    return userPermissions.includes(permission);
  };

  const value: WorkspaceContextType = {
    tenantId,
    user,
    isLoading,
    isAuthenticated: !!user,
    hasPermission,
    refreshUser,
    logout,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextType {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}
