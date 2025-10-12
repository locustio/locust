import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { IStartSwarmResponse, ISwarmFormInput } from 'types/swarm.types';
import {
  IStatsResponse,
  ISwarmExceptionsResponse,
  ISwarmRatios,
  ILogsResponse,
  IWorkerCountResponse,
} from 'types/ui.types';
import { createFormData } from 'utils/object';
import { camelCaseKeys, snakeCaseKeys } from 'utils/string';

const baseQuery = (args: any, api: any, extraOptions: any) =>
  fetchBaseQuery(
    window.baseUrl
      ? {
          baseUrl: window.baseUrl,
          credentials: 'include',
        }
      : undefined,
  )(args, api, extraOptions);

export const api = createApi({
  baseQuery: baseQuery,
  tagTypes: ['stats'],
  endpoints: builder => ({
    getStats: builder.query<IStatsResponse, void>({
      query: () => 'stats/requests',
      transformResponse: camelCaseKeys<IStatsResponse>,
      providesTags: ['stats'],
    }),
    getTasks: builder.query<ISwarmRatios, void>({
      query: () => 'tasks',
      transformResponse: camelCaseKeys<ISwarmRatios>,
    }),
    getExceptions: builder.query<ISwarmExceptionsResponse, void>({
      query: () => 'exceptions',
      transformResponse: camelCaseKeys<ISwarmExceptionsResponse>,
    }),
    getLogs: builder.query<ILogsResponse, void>({
      query: () => 'logs',
      transformResponse: camelCaseKeys<ILogsResponse>,
    }),
    getWorkerCount: builder.query<IWorkerCountResponse, void>({
      query: () => 'worker-count',
      transformResponse: camelCaseKeys<IWorkerCountResponse>,
    }),

    startSwarm: builder.mutation<IStartSwarmResponse, ISwarmFormInput>({
      query: body => ({
        url: 'swarm',
        method: 'POST',
        body: createFormData(snakeCaseKeys(body)),
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      }),
    }),
    updateUserSettings: builder.mutation({
      query: body => ({
        url: 'user',
        method: 'POST',
        body: snakeCaseKeys(body),
      }),
    }),

    resetStats: builder.mutation<void, void>({
      query: () => ({ url: 'stats/reset' }),
      invalidatesTags: ['stats'],
    }),
    stopSwarm: builder.mutation<void, void>({
      query: () => ({ url: 'stop' }),
    }),
  }),
});

export const {
  useGetStatsQuery,
  useGetTasksQuery,
  useGetExceptionsQuery,
  useGetLogsQuery,
  useGetWorkerCountQuery,
  useStartSwarmMutation,
  useUpdateUserSettingsMutation,
  useStopSwarmMutation,
  useResetStatsMutation,
} = api;
