import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { IDynamicConfig, IUpdateDynamicConfigResponse } from 'types/dynamicConfig.types';
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
  tagTypes: ['stats', 'dynamicConfig'],
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
    // no key transformation: user class and setting names are chosen by the locustfile
    getDynamicConfig: builder.query<IDynamicConfig, void>({
      query: () => 'dynamic-config',
      providesTags: ['dynamicConfig'],
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

    updateDynamicConfig: builder.mutation<IUpdateDynamicConfigResponse, IDynamicConfig>({
      query: body => ({ url: 'dynamic-config', method: 'POST', body }),
      invalidatesTags: ['dynamicConfig'],
    }),

    resetStats: builder.mutation<void, void>({
      query: () => ({ url: 'stats/reset', method: 'POST' }),
      invalidatesTags: ['stats'],
    }),
    stopSwarm: builder.mutation<void, void>({
      query: () => ({ url: 'stop', method: 'POST' }),
    }),
  }),
});

export const {
  useGetStatsQuery,
  useGetTasksQuery,
  useGetExceptionsQuery,
  useGetLogsQuery,
  useGetWorkerCountQuery,
  useGetDynamicConfigQuery,
  useStartSwarmMutation,
  useUpdateUserSettingsMutation,
  useUpdateDynamicConfigMutation,
  useStopSwarmMutation,
  useResetStatsMutation,
} = api;
