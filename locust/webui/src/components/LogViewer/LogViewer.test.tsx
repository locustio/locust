import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test } from 'vitest';

import LogViewer from 'components/LogViewer/LogViewer';
import { TEST_BASE_API } from 'test/constants';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

const server = setupServer(
  http.get(`${TEST_BASE_API}/logs`, () => HttpResponse.json({ logs: ['Log 1', 'Log 2', 'Log 3'] })),
);

describe('LogViewer', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should render host, status, RPS, and failures on first load', async () => {
    const { getByText } = renderWithProvider(<LogViewer />, {
      swarm: swarmStateMock,
    });

    await waitFor(() => {
      expect(getByText('Log 1')).toBeTruthy();
      expect(getByText('Log 2')).toBeTruthy();
      expect(getByText('Log 3')).toBeTruthy();
    });
  });
});
