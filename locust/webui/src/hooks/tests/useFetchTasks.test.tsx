import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test } from 'vitest';

import { SWARM_STATE } from 'constants/swarm';
import useFetchTasks from 'hooks/useFetchTasks';
import { TEST_BASE_API } from 'test/constants';
import { ratiosResponseMock, tasksResponseTransformed } from 'test/mocks/statsRequest.mock';
import { renderWithProvider } from 'test/testUtils';

const server = setupServer(
  http.get(`${TEST_BASE_API}/tasks`, () => HttpResponse.json(ratiosResponseMock)),
);

function MockHook() {
  useFetchTasks();

  return <div />;
}

describe('useFetchTasks', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should fetch ratios and update UI accordingly', async () => {
    const { store } = renderWithProvider(<MockHook />, {
      swarm: { state: SWARM_STATE.RUNNING },
    });

    await waitFor(() => {
      expect(store.getState().ui.ratios.perClass).toEqual(tasksResponseTransformed.perClass);
    });
  });
});
