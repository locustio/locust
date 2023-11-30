import { describe, expect, test } from 'vitest';

import ResponseTimeTable from 'components/ResponseTimeTable/ResponseTimeTable';
import { renderWithProvider } from 'test/testUtils';

const percentilesForTable = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0];
const mockResponseTimes = [
  {
    name: '/test',
    method: 'GET',
    ...percentilesForTable.reduce(
      (percentilesData, percentile, index) => ({ ...percentilesData, [percentile]: index }),
      {},
    ),
  },
];

describe('ResponseTimeTable', () => {
  test('renders with correct structure and data', () => {
    const { getByText } = renderWithProvider(
      <ResponseTimeTable responseTimes={mockResponseTimes} />,
    );

    expect(getByText('Method')).toBeTruthy();
    expect(getByText('Name')).toBeTruthy();

    expect(getByText('/test')).toBeTruthy();
    expect(getByText('GET')).toBeTruthy();

    percentilesForTable.forEach((percentile, index) => {
      expect(getByText(`${Number(percentile) * 100}%ile (ms)`)).toBeTruthy();
      expect(getByText(index)).toBeTruthy();
    });
  });
});
