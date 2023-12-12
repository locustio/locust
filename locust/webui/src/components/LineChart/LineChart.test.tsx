import { describe, test, expect } from 'vitest';

import LineChart from 'components/LineChart/LineChart';
import { statsResponseTransformed } from 'test/mocks/statsRequest.mock';
import { renderWithProvider } from 'test/testUtils';
import { ICharts } from 'types/ui.types';

const mockChart = {
  title: 'Total Requests per Second',
  lines: [
    { name: 'RPS', key: 'currentRps' as keyof ICharts },
    { name: 'Failures/s', key: 'currentFailPerSec' as keyof ICharts },
  ],
  colors: ['#00ca5a', '#ff6d6d'],
};

describe('LineChart', () => {
  test('renders LineChart with charts and lines', () => {
    const { container } = renderWithProvider(
      <LineChart
        charts={statsResponseTransformed.charts}
        colors={mockChart.colors}
        lines={mockChart.lines}
        title={mockChart.title}
      />,
    );

    expect(container.querySelector('canvas')).toBeTruthy();
  });
});
