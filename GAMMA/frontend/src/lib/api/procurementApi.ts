import { apiSlice } from './apiSlice';

export const procurementApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getProcurementRequests: builder.query({
      query: (params = {}) => ({
        url: '/procurement/requests',
        params,
      }),
      providesTags: ['Procurement'],
    }),
    getProcurementRequest: builder.query({
      query: (requestId) => `/procurement/requests/${requestId}`,
      providesTags: (result, error, requestId) => [{ type: 'Procurement', id: requestId }],
    }),
    createProcurementRequest: builder.mutation({
      query: (requestData) => ({
        url: '/procurement/requests',
        method: 'POST',
        body: requestData,
      }),
      invalidatesTags: ['Procurement'],
    }),
    updateProcurementRequest: builder.mutation({
      query: ({ requestId, ...updates }) => ({
        url: `/procurement/requests/${requestId}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { requestId }) => [
        { type: 'Procurement', id: requestId },
        'Procurement',
      ],
    }),
    approveProcurementRequest: builder.mutation({
      query: ({ requestId, approvalData }) => ({
        url: `/procurement/requests/${requestId}/approve`,
        method: 'POST',
        body: approvalData,
      }),
      invalidatesTags: (result, error, { requestId }) => [
        { type: 'Procurement', id: requestId },
        'Procurement',
      ],
    }),
    getProcurementWorkflow: builder.query({
      query: () => '/procurement/workflow',
      providesTags: ['ProcurementWorkflow'],
    }),
    updateProcurementWorkflow: builder.mutation({
      query: (workflowData) => ({
        url: '/procurement/workflow',
        method: 'PUT',
        body: workflowData,
      }),
      invalidatesTags: ['ProcurementWorkflow'],
    }),
  }),
});

export const {
  useGetProcurementRequestsQuery,
  useGetProcurementRequestQuery,
  useCreateProcurementRequestMutation,
  useUpdateProcurementRequestMutation,
  useApproveProcurementRequestMutation,
  useGetProcurementWorkflowQuery,
  useUpdateProcurementWorkflowMutation,
} = procurementApi;
