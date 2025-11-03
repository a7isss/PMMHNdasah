import { apiSlice } from './apiSlice';

export const insightsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getProjectInsights: builder.query({
      query: (projectId) => `/insights/projects/${projectId}`,
      providesTags: (result, error, projectId) => [
        { type: 'Insights', id: `project-${projectId}` },
      ],
    }),
    getGlobalInsights: builder.query({
      query: () => '/insights/global',
      providesTags: ['Insights'],
    }),
    getRiskAnalysis: builder.query({
      query: (projectId) => `/insights/risks/${projectId}`,
      providesTags: (result, error, projectId) => [
        { type: 'Insights', id: `risks-${projectId}` },
      ],
    }),
    getCostPredictions: builder.query({
      query: (projectId) => `/insights/costs/${projectId}/predictions`,
      providesTags: (result, error, projectId) => [
        { type: 'Insights', id: `costs-${projectId}` },
      ],
    }),
    getScheduleAnalysis: builder.query({
      query: (projectId) => `/insights/schedule/${projectId}/analysis`,
      providesTags: (result, error, projectId) => [
        { type: 'Insights', id: `schedule-${projectId}` },
      ],
    }),
  }),
});

export const {
  useGetProjectInsightsQuery,
  useGetGlobalInsightsQuery,
  useGetRiskAnalysisQuery,
  useGetCostPredictionsQuery,
  useGetScheduleAnalysisQuery,
} = insightsApi;
