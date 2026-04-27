import { fireEvent, waitFor } from '@testing-library/react';
import { test, describe, expect, vi } from 'vitest';

import Reports, {
  filenameFromContentDisposition,
  injectChartsPngIntoReportHtml,
} from 'components/Reports/Reports';
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

  test('does not render a duplicate client-side charts PNG download', () => {
    const { queryByText } = renderWithProvider(<Reports />, {
      ui: { charts: statsResponseTransformed.charts },
    });

    expect(queryByText('Download charts PNG')).toBeNull();
  });

  test('injects a client-side charts PNG when downloading the report from chart data', async () => {
    const reportHtml =
      '<html><body><script>\n      window.templateArgs = {"is_report":true,"history":[{"time":"2026-04-27T12:00:00Z"}]}\n      window.theme = "light"\n    </script><script type="module" src="/assets/report.js"></script></body></html>';
    const fetchMock = vi.fn().mockResolvedValue({
      headers: {
        get: vi.fn().mockReturnValue('attachment; filename="Locust_report_with_charts.html"'),
      },
      ok: true,
      text: vi.fn().mockResolvedValue(reportHtml),
    });
    type DownloadedBlob = { parts: BlobPart[]; type: string };

    const downloadedAnchor = { current: null as HTMLAnchorElement | null };
    const downloadedBlob = { current: null as DownloadedBlob | null };
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
    const createObjectURL = vi.fn().mockImplementation((blob: DownloadedBlob) => {
      downloadedBlob.current = blob;
      return 'blob:locust-report';
    });
    const revokeObjectURL = vi.fn();
    const originalCreateObjectURL = URL.createObjectURL;
    const originalRevokeObjectURL = URL.revokeObjectURL;

    vi.stubGlobal(
      'Blob',
      class {
        parts: BlobPart[];
        type: string;

        constructor(parts: BlobPart[], options?: BlobPropertyBag) {
          this.parts = parts;
          this.type = options?.type || '';
        }
      },
    );
    vi.stubGlobal('fetch', fetchMock);
    Object.defineProperty(URL, 'createObjectURL', {
      configurable: true,
      value: createObjectURL,
    });
    Object.defineProperty(URL, 'revokeObjectURL', {
      configurable: true,
      value: revokeObjectURL,
    });

    try {
      const { getByText } = renderWithProvider(<Reports />, {
        ui: { charts: statsResponseTransformed.charts },
      });

      fireEvent.click(getByText('Download Report'));

      await waitFor(() =>
        expect(fetchMock).toHaveBeenCalledWith('./stats/report?download=1&theme=light'),
      );
      await waitFor(() => expect(downloadedBlob.current).toBeTruthy());

      expect(downloadedAnchor.current?.download).toBe('Locust_report_with_charts.html');
      expect(downloadedAnchor.current?.href).toBe('blob:locust-report');
      expect(revokeObjectURL).toHaveBeenCalledWith('blob:locust-report');

      const downloadedHtml = downloadedBlob.current?.parts.join('');

      expect(downloadedHtml).toBeTruthy();
      if (!downloadedHtml) {
        return;
      }

      expect(downloadedHtml).toContain('charts_png');
      expect(downloadedHtml).toContain('data:image/png');
      expect(downloadedHtml).toContain('"history":[]');
      expect(downloadedHtml).not.toContain('2026-04-27T12:00:00Z');
      expect(downloadedHtml.indexOf('charts_png')).toBeLessThan(
        downloadedHtml.indexOf('<script type="module"'),
      );
    } finally {
      vi.unstubAllGlobals();
      appendChildSpy.mockRestore();
      clickSpy.mockRestore();
      Object.defineProperty(URL, 'createObjectURL', {
        configurable: true,
        value: originalCreateObjectURL,
      });
      Object.defineProperty(URL, 'revokeObjectURL', {
        configurable: true,
        value: originalRevokeObjectURL,
      });
    }
  });

  test('keeps the normal report link when chart data is unavailable', () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    const { getByText } = renderWithProvider(<Reports />);

    fireEvent.click(getByText('Download Report'));

    expect(fetchMock).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });

  test('adds the chart PNG to report template args and omits chart history', () => {
    const reportHtml =
      '<html><body><script>\n      window.templateArgs = {"is_report":true,"history":[{"time":"2026-04-27T12:00:00Z"}]}\n      window.theme = "light"\n    </script><script type="module" src="/assets/report.js"></script></body></html>';

    const injectedHtml = injectChartsPngIntoReportHtml(reportHtml, 'data:image/png;base64,test');

    expect(injectedHtml).toContain('"charts_png":"data:image/png;base64,test"');
    expect(injectedHtml).toContain('"history":[]');
    expect(injectedHtml).not.toContain('2026-04-27T12:00:00Z');
    expect(injectedHtml.indexOf('charts_png')).toBeLessThan(
      injectedHtml.indexOf('<script type="module"'),
    );
  });

  test('uses the report fallback filename when the report response has no filename header', () => {
    expect(filenameFromContentDisposition(null)).toBe('Locust_report.html');
    expect(filenameFromContentDisposition('attachment')).toBe('Locust_report.html');
  });

  test('uses the report filename from the content disposition header', () => {
    expect(filenameFromContentDisposition('attachment; filename="Locust_2026.html"')).toBe(
      'Locust_2026.html',
    );
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
