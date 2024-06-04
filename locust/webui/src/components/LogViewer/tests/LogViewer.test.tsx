import { describe, expect, test } from 'vitest';

import LogViewer from 'components/LogViewer/LogViewer';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

describe('LogViewer', () => {
  test('should render master logs', () => {
    const masterLogs = ['Log 1', 'Log 2', 'Log 3'];
    const { getByText } = renderWithProvider(<LogViewer />, {
      swarm: swarmStateMock,
      logViewer: {
        master: masterLogs,
        workers: {},
      },
    });

    masterLogs.forEach(log => {
      expect(getByText(log)).toBeTruthy();
    });
  });

  test('should render worker logs when provided', () => {
    const workerId = '123';
    const workerLogs = ['Worker Log 1', 'Worker Log 2'];

    const { getByText } = renderWithProvider(<LogViewer />, {
      swarm: swarmStateMock,
      logViewer: {
        master: [],
        workers: {
          [workerId]: workerLogs,
        },
      },
    });

    expect(getByText('Worker Logs')).toBeTruthy();
    expect(getByText(workerId)).toBeTruthy();
    workerLogs.forEach(log => {
      expect(getByText(log)).toBeTruthy();
    });
  });

  test('should not render worker logs when none are provided', () => {
    const { queryByText } = renderWithProvider(<LogViewer />, {
      swarm: swarmStateMock,
      logViewer: {
        master: ['Log 1', 'Log 2', 'Log 3'],
        workers: {},
      },
    });

    expect(queryByText('Worker Logs')).toBeFalsy();
  });
});
