import { test, describe, expect } from 'vitest';

import Reports from 'components/Reports/Reports';
import { renderWithProvider } from 'test/testUtils';

describe('Reports', () => {
  test('renders a link to download requests CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download requests CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/stats/requests/csv');
  });

  test('renders a link to download failures CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download failures CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/stats/failures/csv');
  });

  test('renders a link to download exceptions CSV', () => {
    const { getByText } = renderWithProvider(<Reports />);

    const link = getByText('Download exceptions CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/exceptions/csv');
  });

  test('renders a link to download stats history CSV when enabled', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      swarm: {
        statsHistoryEnabled: true,
      },
    });

    const link = getByText('Download full request statistics history CSV');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/stats/requests_full_history/csv');
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
    expect(link.getAttribute('href')).toBe('/stats/report?theme=dark');
  });

  test('renders a link to download the report in light mode when theme is light', () => {
    const { getByText } = renderWithProvider(<Reports />, {
      theme: { isDarkMode: false },
    });

    const link = getByText('Download Report');

    expect(link).toBeTruthy();
    expect(link.getAttribute('href')).toBe('/stats/report?theme=light');
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
