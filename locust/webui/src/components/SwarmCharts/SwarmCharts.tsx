import { connect } from 'react-redux';

import LineChart, { ILineChartProps } from 'components/LineChart/LineChart';
import { swarmTemplateArgs } from 'constants/swarm';
import { IRootState } from 'redux/store';
import { ICharts } from 'types/ui.types';

const percentilesToChartLines = swarmTemplateArgs.percentilesToChart
  ? swarmTemplateArgs.percentilesToChart.map(percentile => ({
      name: `${percentile * 100}th percentile`,
      key: `responseTimePercentile${percentile}` as keyof ICharts,
    }))
  : [];

// Allows for the average stat to be shown in a different color than percentiles
const percentileColors = ['#9966CC', '#8A2BE2', '#8E4585', '#E0B0FF', '#C8A2C8', '#E6E6FA']
  .slice(0, percentilesToChartLines.length)
  .concat('#eeff00');

const availableSwarmCharts: ILineChartProps[] = [
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
    lines: [
      ...percentilesToChartLines,
      { name: 'Average Response Time', key: 'totalAvgResponseTime' },
    ],
    colors: percentileColors,
  },
  {
    title: 'Number of Users',
    lines: [{ name: 'Number of Users', key: 'userCount' }],
    colors: ['#0099ff'],
  },
];

export function SwarmCharts({ charts }: { charts: ICharts }) {
  return (
    <div>
      {availableSwarmCharts.map((lineChartProps, index) => (
        <LineChart key={`swarm-chart-${index}`} {...lineChartProps} charts={charts} />
      ))}
    </div>
  );
}

const storeConnector = ({ ui: { charts } }: IRootState) => ({ charts });

export default connect(storeConnector)(SwarmCharts);
