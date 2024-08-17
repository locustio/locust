import { waitFor } from '@testing-library/react';
import { SWARM_STATE } from 'lib';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test } from 'vitest';

import useFetchExceptions from 'hooks/useFetchExceptions';
import { TEST_BASE_API } from 'test/constants';
import { exceptionsResponseMock } from 'test/mocks/statsRequest.mock';
import { renderWithProvider } from 'test/testUtils';

const server = setupServer(
  http.get(`${TEST_BASE_API}/exceptions`, () => HttpResponse.json(exceptionsResponseMock)),
);

function MockHook() {
  useFetchExceptions();

  return <div />;
}

describe('useFetchExceptions', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should fetch exceptions and update UI accordingly', async () => {
    const { store } = renderWithProvider(<MockHook />, {
      swarm: { state: SWARM_STATE.RUNNING },
    });

    await waitFor(() => {
      if (!store.getState().ui.exceptions.length) {
        throw new Error();
      }
    });

    expect(store.getState().ui.exceptions[0]).toEqual(exceptionsResponseMock.exceptions[0]);
  });
});
