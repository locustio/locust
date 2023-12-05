import { describe, expect, test } from 'vitest';

import LogViewer from 'components/LogViewer/LogViewer';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

describe('LogViewer', () => {
  test('should render host, status, RPS, and failures on first load', async () => {
    const { getByText } = renderWithProvider(<LogViewer />, {
      swarm: swarmStateMock,
      logViewer: {
        logs: ['Log 1', 'Log 2', 'Log 3'],
      },
    });

    expect(getByText('Log 1')).toBeTruthy();
    expect(getByText('Log 2')).toBeTruthy();
    expect(getByText('Log 3')).toBeTruthy();
  });
});
