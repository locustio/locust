import { ICharts } from 'types/ui.types';

export type MockChartType = Pick<ICharts, 'currentRps' | 'currentFailPerSec'>;

export const mockChartLines = [
  { name: 'RPS', key: 'currentRps' as keyof MockChartType },
  { name: 'Failures/s', key: 'currentFailPerSec' as keyof MockChartType },
];

export const mockCharts: MockChartType = {
  currentRps: [
    ['Tue, 06 Aug 2024 11:33:02 GMT', 3],
    ['Tue, 06 Aug 2024 11:33:08 GMT', 3.1],
    ['Tue, 06 Aug 2024 11:33:10 GMT', 3.27],
    ['Tue, 06 Aug 2024 11:33:12 GMT', 3.62],
    ['Tue, 06 Aug 2024 11:33:14 GMT', 4.19],
  ],
  currentFailPerSec: [
    ['Tue, 06 Aug 2024 11:33:02 GMT', 0],
    ['Tue, 06 Aug 2024 11:33:08 GMT', 0],
    ['Tue, 06 Aug 2024 11:33:10 GMT', 0],
    ['Tue, 06 Aug 2024 11:33:12 GMT', 0],
    ['Tue, 06 Aug 2024 11:33:14 GMT', 0],
  ],
};

export const mockTimestamps = [
  'Tue, 06 Aug 2024 11:33:02 GMT',
  'Tue, 06 Aug 2024 11:33:08 GMT',
  'Tue, 06 Aug 2024 11:33:10 GMT',
  'Tue, 06 Aug 2024 11:33:12 GMT',
  'Tue, 06 Aug 2024 11:33:14 GMT',
];

export const mockSeriesData = [
  { type: 'line', name: 'RPS', data: mockCharts.currentRps, symbolSize: 4 },
  { type: 'line', name: 'Failures/s', data: mockCharts.currentFailPerSec, symbolSize: 4 },
];

export const mockScatterplotSeriesData = [
  { ...mockSeriesData[0], type: 'scatter' },
  { ...mockSeriesData[1], type: 'scatter' },
];

export const mockTooltipParams = [
  {
    axisValue: 'Tue, 06 Aug 2024 11:33:02 GMT',
    color: '#ff0',
    seriesName: 'RPS',
    value: ['Tue, 06 Aug 2024 11:33:08 GMT', 1] as [string, number],
  },
  {
    axisValue: 'Tue, 06 Aug 2024 11:33:08 GMT',
    color: '#0ff',
    seriesName: 'User',
    value: ['Tue, 06 Aug 2024 11:33:12 GMT', 10] as [string, number],
  },
];
