import { describe, test, expect } from 'vitest';

import LineChart from 'components/LineChart/LineChart';
import { mockChartLines } from 'components/LineChart/tests/LineChart.mocks';
import { statsResponseTransformed } from 'test/mocks/statsRequest.mock';
import { renderWithProvider } from 'test/testUtils';
import { ICharts } from 'types/ui.types';

const mockChart = {
  title: 'Total Requests per Second',
  lines: mockChartLines,
  colors: ['#00ca5a', '#ff6d6d'],
};

describe('LineChart', () => {
  test('renders LineChart with charts and lines', () => {
    const { container } = renderWithProvider(
      <LineChart<ICharts>
        charts={statsResponseTransformed.charts}
        colors={mockChart.colors}
        lines={mockChart.lines}
        title={mockChart.title}
      />,
    );

    expect(container.querySelector('canvas')).toBeTruthy();
  });

  test('renders LineChart with charts and lines as a scatterplot', () => {
    const { container } = renderWithProvider(
      <LineChart<ICharts>
        charts={statsResponseTransformed.charts}
        colors={mockChart.colors}
        lines={mockChart.lines}
        scatterplot
        title={mockChart.title}
      />,
    );

    expect(container.querySelector('canvas')).toBeTruthy();
  });
});
