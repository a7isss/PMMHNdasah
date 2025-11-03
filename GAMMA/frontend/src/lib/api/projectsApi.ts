import { apiSlice } from './apiSlice';

export const projectsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getProjects: builder.query({
      query: (params = {}) => ({
        url: '/projects',
        params,
      }),
      providesTags: ['Projects'],
    }),
    getProject: builder.query({
      query: (projectId) => `/projects/${projectId}`,
      providesTags: (result, error, projectId) => [{ type: 'Projects', id: projectId }],
    }),
    createProject: builder.mutation({
      query: (projectData) => ({
        url: '/projects',
        method: 'POST',
        body: projectData,
      }),
      invalidatesTags: ['Projects'],
    }),
    updateProject: builder.mutation({
      query: ({ projectId, ...updates }) => ({
        url: `/projects/${projectId}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { projectId }) => [
        { type: 'Projects', id: projectId },
        'Projects',
      ],
    }),
    deleteProject: builder.mutation({
      query: (projectId) => ({
        url: `/projects/${projectId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Projects'],
    }),
    getProjectDashboard: builder.query({
      query: (projectId) => `/projects/${projectId}/dashboard`,
      providesTags: (result, error, projectId) => [
        { type: 'Projects', id: `${projectId}-dashboard` },
      ],
    }),
    getProjectHealth: builder.query({
      query: (projectId) => `/projects/${projectId}/health`,
      providesTags: (result, error, projectId) => [
        { type: 'Projects', id: `${projectId}-health` },
      ],
    }),
  }),
});

export const {
  useGetProjectsQuery,
  useGetProjectQuery,
  useCreateProjectMutation,
  useUpdateProjectMutation,
  useDeleteProjectMutation,
  useGetProjectDashboardQuery,
  useGetProjectHealthQuery,
} = projectsApi;
