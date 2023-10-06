import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';
import {
  ICharts,
  ISwarmError,
  ISwarmStat,
  ISwarmRatios,
  ISwarmException,
  ISwarmWorker,
  IExtendedStat,
} from 'types/ui.types';
import { updateArraysAtProps } from 'utils/object';
import { camelCaseKeys } from 'utils/string';

export interface IUiState {
  extendedStats?: IExtendedStat[];
  totalRps: number;
  failRatio: number;
  stats: ISwarmStat[];
  errors: ISwarmError[];
  workers?: ISwarmWorker[];
  exceptions: ISwarmException[];
  ratios: ISwarmRatios;
  charts: ICharts;
  userCount: number;
}

export type UiAction = PayloadAction<Partial<IUiState>>;

const initialState = {
  totalRps: 0,
  failRatio: 0,
  stats: [],
  errors: [],
  exceptions: [],
  charts: camelCaseKeys(window.templateArgs).history.reduce(updateArraysAtProps, {}),
  ratios: {},
  userCount: 0,
};

const addSpaceToChartsBetweenTests = (charts: ICharts, time: string) => {
  return updateArraysAtProps(charts, {
    currentRps: { value: null },
    currentFailPerSec: { value: null },
    responseTimePercentile1: { value: null },
    responseTimePercentile2: { value: null },
    userCount: { value: null },
    time: time,
  });
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setUi: updateStateWithPayload,
    updateCharts: (state, { payload }) => ({
      ...state,
      charts: updateArraysAtProps<ICharts>(state.charts as ICharts, payload),
    }),
    updateChartMarkers: (state, { payload }) => {
      return {
        ...state,
        charts: {
          ...addSpaceToChartsBetweenTests(
            state.charts as ICharts,
            payload.length ? payload.at(-1) : (state.charts as ICharts).time[0],
          ),
          markers: (state.charts as ICharts).markers
            ? [...((state.charts as ICharts).markers as string[]), payload]
            : [(state.charts as ICharts).time[0], payload],
        },
      };
    },
  },
});

export const uiActions = uiSlice.actions;
export default uiSlice.reducer;
