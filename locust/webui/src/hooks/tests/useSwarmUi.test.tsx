import { act, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test, vi } from 'vitest';

import { SWARM_STATE } from 'constants/swarm';
import useSwarmUi from 'hooks/useSwarmUi';
import { swarmActions } from 'redux/slice/swarm.slice';
import { TEST_BASE_API } from 'test/constants';
import {
  ratiosResponseMock,
  statsResponseTransformed,
  statsResponseMock,
  exceptionsResponseMock,
  mockDate,
} from 'test/mocks/statsRequest.mock';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';
import { ICharts } from 'types/ui.types';

const server = setupServer(
  http.get(`${TEST_BASE_API}/stats/requests`, () => HttpResponse.json(statsResponseMock)),
  http.get(`${TEST_BASE_API}/tasks`, () => HttpResponse.json(ratiosResponseMock)),
  http.get(`${TEST_BASE_API}/exceptions`, () => HttpResponse.json(exceptionsResponseMock)),
);

function MockHook() {
  useSwarmUi();

  return <div />;
}

describe('useSwarmUi', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should fetch request stats, ratios, and exceptions and update UI accordingly', async () => {
    vi.useFakeTimers();

    vi.setSystemTime(mockDate);

    const { store } = renderWithProvider(<MockHook />);

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(store.getState().ui).toEqual(statsResponseTransformed);

    vi.useRealTimers();
  });

  test('should add markers to charts between tests', async () => {
    vi.useFakeTimers();

    const testStopTime = new Date().toLocaleTimeString();

    const { store } = renderWithProvider(<MockHook />, {
      swarm: {
        ...swarmStateMock,
        state: SWARM_STATE.STOPPED,
      },
    });

    act(() => {
      store.dispatch(swarmActions.setSwarm({ state: SWARM_STATE.RUNNING }));
    });

    vi.advanceTimersByTime(2000);

    waitFor(() => {
      const testStartTime = new Date().toLocaleTimeString();

      expect((store.getState().ui.charts as ICharts).markers).toEqual([
        testStopTime,
        testStartTime,
      ]);

      vi.useRealTimers();
    });
  });
});
