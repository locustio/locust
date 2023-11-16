import { describe, expect, test } from 'vitest';

import SwarmMonitor from 'components/Layout/Navbar/SwarmMonitor';
import { SWARM_STATE } from 'constants/swarm';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

const mockUiState = {
  totalRps: '5',
  failRatio: '3',
  stats: [],
  errors: [],
  exceptions: [],
  charts: [],
  ratios: {},
  userCount: '2',
};

describe('SwarmMonitor', () => {
  test('should render host, status, RPS, and failures on first load', () => {
    const { getByText } = renderWithProvider(<SwarmMonitor />, { swarm: swarmStateMock });

    expect(getByText('Host').nextElementSibling?.textContent).toBe(swarmStateMock.host);
    expect(getByText('Status').nextElementSibling?.textContent).toBe(SWARM_STATE.READY);
    expect(getByText('RPS').nextElementSibling?.textContent).toBe('0');
    expect(getByText('Failures').nextElementSibling?.textContent).toBe('0%');
  });

  test('should not render users on first load', () => {
    const { queryByText } = renderWithProvider(<SwarmMonitor />, { swarm: swarmStateMock });

    expect(queryByText('Users')).toBeNull();
    expect(queryByText('Workers')).toBeNull();
  });

  test('should render host, status, Users, RPS, and failures on test run', () => {
    const { getByText } = renderWithProvider(<SwarmMonitor />, {
      swarm: { ...swarmStateMock, state: SWARM_STATE.RUNNING },
      ui: mockUiState,
    });

    expect(getByText('Host').nextElementSibling?.textContent).toBe(swarmStateMock.host);
    expect(getByText('Status').nextElementSibling?.textContent).toBe(SWARM_STATE.RUNNING);
    expect(getByText('RPS').nextElementSibling?.textContent).toBe(mockUiState.totalRps);
    expect(getByText('Users').nextElementSibling?.textContent).toBe(mockUiState.userCount);
    expect(getByText('Failures').nextElementSibling?.textContent).toBe(`${mockUiState.failRatio}%`);
  });

  test('should render workers on distributed test run', () => {
    const mockDistributedState = {
      isDistributed: true,
      workerCount: '1',
    };

    const { getByText } = renderWithProvider(<SwarmMonitor />, {
      swarm: { ...swarmStateMock, ...mockDistributedState, state: SWARM_STATE.RUNNING },
      ui: mockUiState,
    });

    expect(getByText('Workers')).toBeTruthy();
    expect(getByText('Workers').nextElementSibling?.textContent).toBe(
      mockDistributedState.workerCount,
    );
  });

  test('should not render workers when test is not distributed', () => {
    const { queryByText } = renderWithProvider(<SwarmMonitor />);

    expect(queryByText('Workers')).toBeNull();
  });
});
