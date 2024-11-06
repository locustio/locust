import { describe, expect, test } from 'vitest';

import HtmlReport from 'pages/HtmlReport';
import { swarmReportMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';
import { formatLocaleString } from 'utils/date';

describe('HtmlReport', () => {
  test('renders a report', () => {
    const { getByRole, getByText } = renderWithProvider(<HtmlReport {...swarmReportMock} />);

    expect(getByRole('heading', { name: 'Locust Test Report' })).toBeTruthy();
    expect(getByRole('heading', { name: 'Request Statistics' })).toBeTruthy();
    expect(getByRole('heading', { name: 'Failures Statistics' })).toBeTruthy();
    expect(getByRole('heading', { name: 'Charts' })).toBeTruthy();
    expect(getByRole('heading', { name: 'Final ratio' })).toBeTruthy();
    expect(getByRole('link', { name: 'Download the Report' }));
    expect(getByText(swarmReportMock.locustfile)).toBeTruthy();
    expect(getByText(swarmReportMock.host)).toBeTruthy();
  });

  test('formats the start and end time as expected', () => {
    const { getByText } = renderWithProvider(<HtmlReport {...swarmReportMock} />);

    expect(
      getByText(
        `${formatLocaleString(swarmReportMock.startTime)} - ${formatLocaleString(
          swarmReportMock.endTime,
        )} (${swarmReportMock.duration})`,
      ),
    ).toBeTruthy();
  });

  test('does not render the download link when showDownloadLink is false', () => {
    const { queryByRole } = renderWithProvider(
      <HtmlReport {...swarmReportMock} showDownloadLink={false} />,
    );

    expect(queryByRole('link', { name: 'Download the Report' })).toBeNull();
  });

  test('renders the exceptions table when exceptions are present', () => {
    const exception = {
      count: 1,
      msg: 'Something went wrong',
      nodes: 'local',
      traceback: '',
    };

    const { getByRole, getByText } = renderWithProvider(
      <HtmlReport {...swarmReportMock} exceptionsStatistics={[exception]} />,
    );

    expect(getByRole('heading', { name: 'Exceptions Statistics' })).toBeTruthy();
    expect(getByText(exception.msg)).toBeTruthy();
  });
});
