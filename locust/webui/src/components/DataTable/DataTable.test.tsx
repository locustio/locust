import { describe, expect, test } from 'vitest';

import DataTable from 'components/DataTable/DataTable';
import { renderWithProvider } from 'test/testUtils';

const mockState = {
  swarm: {
    extendedTables: [
      {
        key: 'content-length',
        structure: [
          { key: 'name', title: 'Name' },
          { key: 'content_length', title: 'Total content length' },
        ],
      },
    ],
  },
  ui: {
    extendedStats: [
      {
        key: 'content-length',
        data: [{ name: '/test', safeName: '/test', contentLength: 200 }],
      },
    ],
  },
  url: {
    query: {
      tab: 'content-length',
    },
  },
};

describe('Tabs', () => {
  test('renders DataTable with correct structure and data', () => {
    const { getByText } = renderWithProvider(<DataTable />, mockState);

    expect(getByText('Name')).toBeTruthy();
    expect(getByText('Total content length')).toBeTruthy();
    expect(getByText('/test')).toBeTruthy();
    expect(getByText('200')).toBeTruthy();
  });
});
