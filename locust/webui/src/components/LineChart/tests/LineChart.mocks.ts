import { ICharts } from 'types/ui.types';
import { formatLocaleTime } from 'utils/date';

export type MockChartType = Pick<ICharts, 'currentRps' | 'currentFailPerSec' | 'time'>;

export const mockChartLines = [
  { name: 'RPS', key: 'currentRps' as keyof MockChartType },
  { name: 'Failures/s', key: 'currentFailPerSec' as keyof MockChartType },
];

export const mockCharts = {
  currentRps: [3, 3.1, 3.27, 3.62, 4.19],
  currentFailPerSec: [0, 0, 0, 0, 0],
  time: [
    'Tue, 06 Aug 2024 11:33:02 GMT',
    'Tue, 06 Aug 2024 11:33:08 GMT',
    'Tue, 06 Aug 2024 11:33:10 GMT',
    'Tue, 06 Aug 2024 11:33:12 GMT',
    'Tue, 06 Aug 2024 11:33:14 GMT',
  ],
};

export const mockFormattedTimeAxis = mockCharts.time.map(formatLocaleTime);

export const mockSeriesData = [
  { type: 'line', name: 'RPS', data: mockCharts.currentRps },
  { type: 'line', name: 'Failures/s', data: mockCharts.currentFailPerSec },
];

export const mockTooltipParams = [
  {
    axisValue: 'Tue, 06 Aug 2024 11:33:02 GMT',
    color: '#ff0',
    seriesName: 'RPS',
    value: 1,
  },
  {
    axisValue: 'Tue, 06 Aug 2024 11:33:08 GMT',
    color: '#0ff',
    seriesName: 'User',
    value: 10,
  },
];
