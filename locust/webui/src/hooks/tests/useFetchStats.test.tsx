import { act, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test, vi } from 'vitest';

import { SWARM_STATE } from 'constants/swarm';
import useFetchStats from 'hooks/useFetchStats';
import { swarmActions } from 'redux/slice/swarm.slice';
import { TEST_BASE_API } from 'test/constants';
import { statsResponseTransformed, statsResponseMock } from 'test/mocks/statsRequest.mock';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';
import { ICharts } from 'types/ui.types';

const server = setupServer(
  http.get(`${TEST_BASE_API}/stats/requests`, () => HttpResponse.json(statsResponseMock)),
);

function MockHook() {
  useFetchStats();

  return <div />;
}

describe('useFetchStats', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should fetch request stats and update UI accordingly', async () => {
    const { store } = renderWithProvider(<MockHook />, {
      swarm: { state: SWARM_STATE.RUNNING },
    });

    await waitFor(() => {
      if (!store.getState().ui.stats.length) {
        throw new Error();
      }
    });

    expect(store.getState().ui.stats).toEqual(statsResponseTransformed.stats);
  });

  test('should add markers to charts between tests', async () => {
    vi.useFakeTimers();

    const testStopTime = new Date().toISOString();

    const { store } = renderWithProvider(<MockHook />, {
      swarm: {
        ...swarmStateMock,
        state: SWARM_STATE.STOPPED,
      },
      ui: {
        charts: {
          time: [testStopTime],
        },
      },
    });

    act(() => {
      store.dispatch(swarmActions.setSwarm({ state: SWARM_STATE.RUNNING }));
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });

    const testStartTime = new Date().toISOString();

    expect((store.getState().ui.charts as ICharts).markers).toEqual([testStopTime, testStartTime]);
  });
});
