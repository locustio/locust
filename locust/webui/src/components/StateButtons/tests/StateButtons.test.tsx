import { describe, test, expect } from 'vitest';

import StateButtons from 'components/StateButtons/StateButtons';
import { SWARM_STATE } from 'constants/swarm';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

describe('StateButtons', () => {
  test('does not render anything when swarm state is READY', () => {
    const { container } = renderWithProvider(<StateButtons />);

    expect(container.innerHTML).toEqual('');
  });

  test('renders NewTestButton when swarm state is STOPPED', () => {
    const { queryByText } = renderWithProvider(<StateButtons />, {
      swarm: {
        ...swarmStateMock,
        state: SWARM_STATE.STOPPED,
      },
    });

    expect(queryByText('New')).toBeTruthy();
    expect(queryByText('Reset')).toBeTruthy();
    expect(queryByText('Edit')).toBeFalsy();
    expect(queryByText('Stop')).toBeFalsy();
  });

  test('renders EditButton, StopButton, and ResetButton when swarm state is RUNNING', () => {
    const { queryByText } = renderWithProvider(<StateButtons />, {
      swarm: {
        ...swarmStateMock,
        state: SWARM_STATE.RUNNING,
      },
    });

    expect(queryByText('New')).toBeFalsy();
    expect(queryByText('Edit')).toBeTruthy();
    expect(queryByText('Stop')).toBeTruthy();
    expect(queryByText('Reset')).toBeTruthy();
  });

  test('renders EditButton, StopButton, and ResetButton when swarm state is SPAWNING', () => {
    const { queryByText } = renderWithProvider(<StateButtons />, {
      swarm: {
        ...swarmStateMock,
        state: SWARM_STATE.SPAWNING,
      },
    });

    expect(queryByText('New')).toBeFalsy();
    expect(queryByText('Edit')).toBeTruthy();
    expect(queryByText('Stop')).toBeTruthy();
    expect(queryByText('Reset')).toBeTruthy();
  });
});
