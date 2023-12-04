import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, test } from 'vitest';

import useLogViewer from 'components/LogViewer/useLogViewer';
import { TEST_BASE_API } from 'test/constants';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

const mockLogs = ['Log 1', 'Log 2', 'Log 3'];

const server = setupServer(
  http.get(`${TEST_BASE_API}/logs`, () => HttpResponse.json({ logs: mockLogs })),
);

function MockHook() {
  const logs = useLogViewer();

  return <span data-testid='logs'>{JSON.stringify(logs)}</span>;
}

describe('useLogViewer', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should fetch logs from server and store them in state', async () => {
    const { store, getByTestId } = renderWithProvider(<MockHook />, {
      swarm: swarmStateMock,
    });

    await waitFor(() => {
      expect(getByTestId('logs').textContent).toBe(JSON.stringify(mockLogs));
      expect(store.getState().logViewer.logs).toEqual(mockLogs);
    });
  });
});
