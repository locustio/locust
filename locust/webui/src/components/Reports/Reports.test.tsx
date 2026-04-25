import { fireEvent, waitFor } from '@testing-library/react';
import { test, describe, expect, vi } from 'vitest';

import Reports from 'components/Reports/Reports';
import { SWARM_CHART_COUNT } from 'components/SwarmCharts/SwarmCharts';
import { statsResponseTransformed } from 'test/mocks/statsRequest.mock';
import { renderWithProvider } from 'test/testUtils';

describe('Reports', () => {
  test('renders a link to download requests CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download requests CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./stats/requests/csv');
  });

  test('renders a link to download failures CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download failures CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./stats/failures/csv');
  });

  test('renders a link to download exceptions CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download exceptions CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./exceptions/csv');
  });

  test('renders a link to download stats history CSV when enabled', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      swarm: {
        statsHistoryEnabled: true,
      },
    });

    const link = getByText('Download full request statistics history CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./stats/requests_full_history/csv');
  });

  test('does not render a link to download stats history CSV when disabled', () => {
    const { queryByText } = renderWithProvider(<Reports />, {
      swarm: { statsHistoryEnabled: false },
    });

    expect(queryByText('Download full request statistics history CSV')).toBeNull();
  });

  test('renders a link to download the report in dark mode when theme is dark', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      theme: { isDarkMode: true },
    });

    const link = getByText('Download Report');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./stats/report?theme=dark');
  });

  test('renders a link to download the report in light mode when theme is light', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      theme: { isDarkMode: false },
    });

    const link = getByText('Download Report');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('./stats/report?theme=light');
  });

  test('renders a client-side charts PNG download when chart data is available', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      ui: { charts: statsResponseTransformed.charts },
    });

    const link = getByText('Download charts PNG');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBeNull();
  });

  test('downloads a client-side charts PNG from rendered chart data', async () => {
    const { container, getByText } = renderWithProvider(<Reports />, {
      ui: { charts: statsResponseTransformed.charts },
    });

    await waitFor(() =>
      expect(container.querySelectorAll('canvas').length).toBe(SWARM_CHART_COUNT),
    );

    const downloadedAnchor = { current: null as HTMLAnchorElement | null };
    const appendChild = document.body.appendChild.bind(document.body);
    const appendChildSpy = vi
      .spyOn(document.body, 'appendChild')
      .mockImplementation(<T extends Node>(node: T) => {
        if (node instanceof HTMLAnchorElement) {
          downloadedAnchor.current = node;
        }

        return appendChild(node) as T;
      });
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});

    try {
      await waitFor(() => {
        fireEvent.click(getByText('Download charts PNG'));
        expect(downloadedAnchor.current).toBeTruthy();
      });

      expect(downloadedAnchor.current?.download).toMatch(/^Locust_charts_.*\.png$/);
      expect(downloadedAnchor.current?.href).toMatch(/^data:image\/png/);
    } finally {
      appendChildSpy.mockRestore();
      clickSpy.mockRestore();
    }
  });

  test('does not render a client-side charts PNG download when chart data is unavailable', () => {
    const { queryByText } = renderWithProvider(<Reports />);

    expect(queryByText('Download charts PNG')).toBeNull();
  });

  test('renders links to download extended CSV files', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      swarm: {
        extendedCsvFiles: [
          { href: '/content-length/csv', title: 'Download content length statistics CSV' },
        ],
      },
    });

    const link = getByText('Download content length statistics CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/content-length/csv');
  });

  test('does not render extended CSV files when there are none', () => {
    const { queryByText } = renderWithProvider(<Reports />);

    expect(queryByText('Download content length statistics CSV')).toBeNull();
  });
});
