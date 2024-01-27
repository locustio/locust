import { describe, expect, test } from 'vitest';

import uiSlice, { IUiState, UiAction, uiActions } from 'redux/slice/ui.slice';
import { percentilesToChart } from 'test/mocks/swarmState.mock';
import { ICharts, ISwarmRatios } from 'types/ui.types';

const responseTimePercentileKey1 =
  `responseTimePercentile${percentilesToChart[0]}` as `responseTimePercentile${number}`;
const responseTimePercentileKey2 =
  `responseTimePercentile${percentilesToChart[1]}` as `responseTimePercentile${number}`;

const initialState = {
  totalRps: 0,
  failRatio: 0,
  stats: [],
  errors: [],
  exceptions: [],
  charts: {
    [responseTimePercentileKey1]: [],
    [responseTimePercentileKey1]: [],
    currentRps: [],
    currentFailPerSec: [],
    totalAvgResponseTime: [],
    userCount: [],
    time: [],
  },
  ratios: {} as ISwarmRatios,
  userCount: 0,
};

describe('uiSlice', () => {
  test('should set UI state', () => {
    const action = (uiActions.setUi as (payload: Partial<IUiState>) => UiAction)({
      totalRps: 100,
      userCount: 50,
    });
    const nextState = uiSlice(initialState, action);
    expect(nextState).toEqual({
      ...initialState,
      totalRps: 100,
      userCount: 50,
    });
  });

  test('should update charts in UI state', () => {
    const action = uiActions.updateCharts({
      currentRps: 5,
      currentFailPerSec: 1,
      [responseTimePercentileKey1]: 0.4,
      [responseTimePercentileKey2]: 0.2,
      userCount: 2,
      time: '10:10:10',
    });

    const nextState = uiSlice(initialState, action);
    const charts = nextState.charts as ICharts;

    expect(charts.currentRps[0]).toBe(5);
    expect(charts.currentFailPerSec[0]).toBe(1);
    expect(charts[responseTimePercentileKey1][0]).toBe(0.4);
    expect(charts[responseTimePercentileKey2][0]).toBe(0.2);
    expect(charts.userCount[0]).toBe(2);
    expect(charts.time[0]).toBe('10:10:10');
  });

  test('should continue to extend the corresponding array of charts in UI state', () => {
    const action = uiActions.updateCharts({
      currentRps: 5,
      currentFailPerSec: 1,
      [responseTimePercentileKey1]: 0.4,
      [responseTimePercentileKey2]: 0.2,
      userCount: 2,
      time: '10:10:10',
    });

    const updatedState = uiSlice(initialState, action);
    const nextState = uiSlice(updatedState, action);

    const charts = nextState.charts as ICharts;

    expect(charts.currentRps).toEqual([5, 5]);
    expect(charts.currentFailPerSec).toEqual([1, 1]);
    expect(charts[responseTimePercentileKey1]).toEqual([0.4, 0.4]);
    expect(charts[responseTimePercentileKey2]).toEqual([0.2, 0.2]);
    expect(charts.userCount).toEqual([2, 2]);
    expect(charts.time).toEqual(['10:10:10', '10:10:10']);
  });

  test('should update chart markers in UI state', () => {
    const action = uiActions.updateChartMarkers('20:20:20');
    const nextState = uiSlice(
      {
        ...initialState,
        charts: {
          ...initialState.charts,
          time: ['10:10:10'],
        },
      },
      action,
    );

    const charts = nextState.charts as ICharts;

    expect(charts.markers).toEqual(['10:10:10', '20:20:20']);

    // Add space between runs
    expect(charts.currentRps[0]).toEqual({ value: null });
    expect(charts.currentFailPerSec[0]).toEqual({ value: null });
    expect(charts[responseTimePercentileKey1][0]).toEqual({ value: null });
    expect(charts[responseTimePercentileKey2][0]).toEqual({ value: null });
    expect(charts.userCount[0]).toEqual({ value: null });
  });
});
