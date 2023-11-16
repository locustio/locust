import { connect } from 'react-redux';

import LineChart, { ILineChartProps } from 'components/LineChart/LineChart';
import { IRootState } from 'redux/store';
import { ICharts } from 'types/ui.types';

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
      {
        name: `${window.templateArgs.percentile1 * 100}th percentile`,
        key: 'responseTimePercentile1',
      },
      {
        name: `${window.templateArgs.percentile2 * 100}th percentile`,
        key: 'responseTimePercentile2',
      },
    ],
  },
  {
    title: 'Number of Users',
    lines: [{ name: 'Number of Users', key: 'userCount' }],
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
