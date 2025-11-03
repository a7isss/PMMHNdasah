import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store';

export interface Tenant {
  id: string;
  name: string;
  domain?: string;
  subscription_plan: string;
  is_active: boolean;
  contact_email?: string;
  contact_phone?: string;
  user_count: number;
  created_at: string;
  updated_at: string;
}

export interface TenantDetails extends Tenant {
  address?: any;
  settings: any;
  ai_config: any;
  statistics: {
    total_users: number;
    active_users: number;
    total_projects: number;
  };
}

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  role: string;
  is_active: boolean;
  is_email_verified: boolean;
  whatsapp_verified: boolean;
  whatsapp_number?: string;
  last_login_at?: string;
  tenant: {
    id: string;
    name: string;
    domain?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface UserDetails extends User {
  phone?: string;
  job_title?: string;
  avatar_url?: string;
  permissions?: string[];
  preferences: any;
  whatsapp_number?: string;
  ai_profile: any;
}

export interface AdminStats {
  tenants: {
    total: number;
    active: number;
    inactive: number;
    new_last_30_days: number;
  };
  users: {
    total: number;
    active: number;
    inactive: number;
    new_last_30_days: number;
  };
  roles: Record<string, number>;
  system_health: {
    database_status: string;
    last_updated: string;
  };
}

export interface CreateUserRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  role: string;
  whatsapp_number?: string;
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  avatar_url?: string;
  role?: string;
  whatsapp_number?: string;
  is_active?: boolean;
}

export interface UpdateTenantRequest {
  name?: string;
  domain?: string;
  subscription_plan?: string;
  is_active?: boolean;
  contact_email?: string;
  contact_phone?: string;
  address?: any;
  settings?: any;
  ai_config?: any;
}

export interface TenantCreate {
  name: string;
  domain?: string;
  subscription_plan: string;
  contact_email?: string;
  contact_phone?: string;
}

export const adminApi = createApi({
  reducerPath: 'adminApi',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Tenants', 'Users', 'AdminStats'],
  endpoints: (builder) => ({
    // Tenant endpoints
    getTenants: builder.query<{
      tenants: Tenant[];
      total: number;
    }, {
      skip?: number;
      limit?: number;
      search?: string;
      is_active?: boolean;
    }>({
      query: (params) => ({
        url: '/admin/tenants',
        params,
      }),
      providesTags: ['Tenants'],
      transformResponse: (response: Tenant[]) => ({
        tenants: response,
        total: response.length,
      }),
    }),

    getTenantDetails: builder.query<TenantDetails, string>({
      query: (tenantId) => `/admin/tenants/${tenantId}`,
      providesTags: (result, error, tenantId) => [{ type: 'Tenants', id: tenantId }],
    }),

    updateTenant: builder.mutation<{ message: string; tenant: Tenant }, {
      tenantId: string;
      data: UpdateTenantRequest;
    }>({
      query: ({ tenantId, data }) => ({
        url: `/admin/tenants/${tenantId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { tenantId }) => [
        { type: 'Tenants', id: tenantId },
        'Tenants',
      ],
    }),

    deleteTenant: builder.mutation<{ message: string }, string>({
      query: (tenantId) => ({
        url: `/admin/tenants/${tenantId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Tenants', 'Users', 'AdminStats'],
    }),

    createTenant: builder.mutation<Tenant, TenantCreate>({
      query: (tenantData) => ({
        url: '/admin/tenants',
        method: 'POST',
        body: tenantData,
      }),
      invalidatesTags: ['Tenants', 'AdminStats'],
    }),

    // User endpoints
    getUsers: builder.query<{
      users: User[];
      total: number;
    }, {
      skip?: number;
      limit?: number;
      search?: string;
      tenant_id?: string;
      role?: string;
      is_active?: boolean;
    }>({
      query: (params) => ({
        url: '/admin/users',
        params,
      }),
      providesTags: ['Users'],
      transformResponse: (response: User[]) => ({
        users: response,
        total: response.length,
      }),
    }),

    getUserDetails: builder.query<UserDetails, string>({
      query: (userId) => `/admin/users/${userId}`,
      providesTags: (result, error, userId) => [{ type: 'Users', id: userId }],
    }),

    createUser: builder.mutation<{
      message: string;
      user: { id: string; email: string; first_name?: string; last_name?: string; role: string; tenant_name: string };
    }, {
      userData: CreateUserRequest;
      tenantId: string;
    }>({
      query: ({ userData, tenantId }) => ({
        url: '/admin/users',
        method: 'POST',
        body: userData,
        params: { tenant_id: tenantId },
      }),
      invalidatesTags: ['Users', 'AdminStats'],
    }),

    updateUser: builder.mutation<{ message: string }, {
      userId: string;
      data: UpdateUserRequest;
    }>({
      query: ({ userId, data }) => ({
        url: `/admin/users/${userId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'Users', id: userId },
        'Users',
        'AdminStats',
      ],
    }),

    deleteUser: builder.mutation<{ message: string }, string>({
      query: (userId) => ({
        url: `/admin/users/${userId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Users', 'AdminStats'],
    }),

    deactivateUser: builder.mutation<{ message: string }, string>({
      query: (userId) => ({
        url: `/admin/users/${userId}/deactivate`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, userId) => [
        { type: 'Users', id: userId },
        'Users',
        'AdminStats',
      ],
    }),

    activateUser: builder.mutation<{ message: string }, string>({
      query: (userId) => ({
        url: `/admin/users/${userId}/activate`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, userId) => [
        { type: 'Users', id: userId },
        'Users',
        'AdminStats',
      ],
    }),

    // Statistics endpoint
    getAdminStats: builder.query<AdminStats, void>({
      query: () => '/admin/stats',
      providesTags: ['AdminStats'],
    }),
  }),
});

export const {
  useGetTenantsQuery,
  useGetTenantDetailsQuery,
  useUpdateTenantMutation,
  useDeleteTenantMutation,
  useCreateTenantMutation,
  useGetUsersQuery,
  useGetUserDetailsQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useDeactivateUserMutation,
  useActivateUserMutation,
  useGetAdminStatsQuery,
} = adminApi;
