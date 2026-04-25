import type { ECharts } from 'echarts';

import LineChart from 'components/LineChart/LineChart';
import { ILineChart } from 'components/LineChart/LineChart.types';
import { swarmTemplateArgs } from 'constants/swarm';
import { ICharts } from 'types/ui.types';

const percentilesToChartLines = swarmTemplateArgs.percentilesToChart
  ? swarmTemplateArgs.percentilesToChart.map(percentile => ({
      name: `${percentile * 100}th percentile`,
      key: `responseTimePercentile${percentile}` as keyof ICharts,
    }))
  : [];

const percentileColors = [
  '#ff9f00',
  '#9966CC',
  '#8A2BE2',
  '#8E4585',
  '#E0B0FF',
  '#C8A2C8',
  '#E6E6FA',
];

export const availableSwarmCharts: Omit<ILineChart<ICharts>, 'charts'>[] = [
  {
    title: 'Total Requests per Second',
    lines: [
      { name: 'RPS', key: 'currentRps' },
      { name: 'Failures/s', key: 'currentFailPerSec' },
    ],
    colors: ['#00ca5a', '#ff6d6d'],
  },
  {
    title: 'Response Times (ms)',
    lines: percentilesToChartLines,
    colors: percentileColors,
  },
  {
    title: 'Number of Users',
    lines: [{ name: 'Number of Users', key: 'userCount' }],
    colors: ['#0099ff'],
  },
];

export const SWARM_CHART_COUNT = availableSwarmCharts.length;

export default function SwarmCharts({
  charts,
  isDarkMode,
  onChartReady,
  chartGroup,
}: {
  charts: ICharts;
  isDarkMode?: boolean;
  onChartReady?: (chart: ECharts, index: number) => void;
  chartGroup?: string;
}) {
  return availableSwarmCharts.map((lineChartProps, index) => (
    <LineChart<ICharts>
      key={`swarm-chart-${index}`}
      {...lineChartProps}
      chartGroup={chartGroup}
      charts={charts}
      isDarkMode={isDarkMode}
      onChartReady={chart => onChartReady?.(chart, index)}
    />
  ));
}
