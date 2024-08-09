import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterEach, describe, expect, test } from 'vitest';

import useLogViewer from 'components/LogViewer/useLogViewer';
import { TEST_BASE_API } from 'test/constants';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

const mockLogs = {
  master: ['Log 1', 'Log 2', 'Log 3'],
  workers: {
    '123': ['Worker Log'],
  },
};

const mockImportantMasterLog = {
  master: ['Log 1', 'WARNING Log 2', 'Log 3'],
  workers: {
    '123': ['Worker Log'],
  },
};

const mockImportantWorkerLog = {
  master: ['Log 1', 'WARNING Log 2', 'Log 3'],
  workers: {
    '123': ['ERROR Worker Log'],
  },
};

function MockHook() {
  const logs = useLogViewer();

  return <span data-testid='logs'>{JSON.stringify(logs)}</span>;
}

describe('useLogViewer', () => {
  afterEach(() => {
    localStorage.clear();
  });

  test('should fetch logs from server and store them in state', async () => {
    const server = setupServer(
      http.get(`${TEST_BASE_API}/logs`, () => HttpResponse.json(mockLogs)),
    );
    server.listen();

    const { store, getByTestId } = renderWithProvider(<MockHook />, {
      swarm: swarmStateMock,
    });

    await waitFor(() => {
      expect(getByTestId('logs').textContent).toBe(JSON.stringify(mockLogs));
      expect(store.getState().logViewer).toEqual(mockLogs);
    });
    server.resetHandlers();
    server.close();
  });

  test('should set a notification if important logs are present', async () => {
    const server = setupServer(
      http.get(`${TEST_BASE_API}/logs`, () => HttpResponse.json(mockImportantMasterLog)),
    );
    server.listen();

    const { store, getByTestId } = renderWithProvider(<MockHook />, {
      swarm: swarmStateMock,
    });

    await waitFor(() => {
      expect(getByTestId('logs').textContent).toBe(JSON.stringify(mockImportantMasterLog));
      expect(store.getState().logViewer).toEqual(mockImportantMasterLog);
      expect(store.getState().notification).toEqual({ logViewer: true });
    });

    server.close();
  });

  test('should set a notification if important worker logs are present', async () => {
    const server = setupServer(
      http.get(`${TEST_BASE_API}/logs`, () => HttpResponse.json(mockImportantWorkerLog)),
    );
    server.listen();

    const { store, getByTestId } = renderWithProvider(<MockHook />, {
      swarm: swarmStateMock,
    });

    await waitFor(() => {
      expect(getByTestId('logs').textContent).toBe(JSON.stringify(mockImportantWorkerLog));
      expect(store.getState().logViewer).toEqual(mockImportantWorkerLog);
      expect(store.getState().notification).toEqual({ logViewer: true });
    });

    server.close();
  });
});
