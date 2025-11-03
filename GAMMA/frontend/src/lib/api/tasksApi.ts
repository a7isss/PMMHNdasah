import { apiSlice } from './apiSlice';

export const tasksApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getTasks: builder.query({
      query: (params = {}) => ({
        url: '/tasks',
        params,
      }),
      providesTags: ['Tasks'],
    }),
    getTask: builder.query({
      query: (taskId) => `/tasks/${taskId}`,
      providesTags: (result, error, taskId) => [{ type: 'Tasks', id: taskId }],
    }),
    createTask: builder.mutation({
      query: (taskData) => ({
        url: '/tasks',
        method: 'POST',
        body: taskData,
      }),
      invalidatesTags: ['Tasks'],
    }),
    updateTask: builder.mutation({
      query: ({ taskId, ...updates }) => ({
        url: `/tasks/${taskId}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { taskId }) => [
        { type: 'Tasks', id: taskId },
        'Tasks',
      ],
    }),
    deleteTask: builder.mutation({
      query: (taskId) => ({
        url: `/tasks/${taskId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Tasks'],
    }),
    getProjectTasks: builder.query({
      query: (projectId) => `/projects/${projectId}/tasks`,
      providesTags: (result, error, projectId) => [
        { type: 'Tasks', id: `project-${projectId}` },
      ],
    }),
    bulkUpdateTasks: builder.mutation({
      query: (updates) => ({
        url: '/tasks/bulk',
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['Tasks'],
    }),
    getTaskDependencies: builder.query({
      query: (taskId) => `/tasks/${taskId}/dependencies`,
      providesTags: (result, error, taskId) => [
        { type: 'Tasks', id: `${taskId}-dependencies` },
      ],
    }),
    createTaskDependency: builder.mutation({
      query: ({ taskId, dependencyData }) => ({
        url: `/tasks/${taskId}/dependencies`,
        method: 'POST',
        body: dependencyData,
      }),
      invalidatesTags: ['Tasks'],
    }),
  }),
});

export const {
  useGetTasksQuery,
  useGetTaskQuery,
  useCreateTaskMutation,
  useUpdateTaskMutation,
  useDeleteTaskMutation,
  useGetProjectTasksQuery,
  useBulkUpdateTasksMutation,
  useGetTaskDependenciesQuery,
  useCreateTaskDependencyMutation,
} = tasksApi;
