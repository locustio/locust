import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { IStatsResponse, ISwarmExceptionsResponse, ISwarmRatios } from 'types/ui.types';
import { createFormData } from 'utils/object';
import { camelCaseKeys, snakeCaseKeys } from 'utils/string';

export const api = createApi({
  baseQuery: fetchBaseQuery(),
  endpoints: builder => ({
    getStats: builder.query<IStatsResponse, void>({
      query: () => 'stats/requests',
      transformResponse: camelCaseKeys<IStatsResponse>,
    }),
    getTasks: builder.query<ISwarmRatios, void>({
      query: () => 'tasks',
      transformResponse: camelCaseKeys<ISwarmRatios>,
    }),
    getExceptions: builder.query<ISwarmExceptionsResponse, void>({
      query: () => 'exceptions',
      transformResponse: camelCaseKeys<ISwarmExceptionsResponse>,
    }),

    startSwarm: builder.mutation({
      query: body => ({
        url: 'swarm',
        method: 'POST',
        body: createFormData(snakeCaseKeys(body)),
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      }),
    }),
  }),
});

export const { useGetStatsQuery, useGetTasksQuery, useGetExceptionsQuery, useStartSwarmMutation } =
  api;
