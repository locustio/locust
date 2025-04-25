import { act, fireEvent, waitFor } from '@testing-library/react';
import { http } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterAll, describe, test, expect, vi, afterEach } from 'vitest';

import StopButton from 'components/StateButtons/StopButton';
import { TEST_BASE_API } from 'test/constants';
import { renderWithProvider } from 'test/testUtils';

const stopSwarm = vi.fn();

const server = setupServer(
  http.get(`${TEST_BASE_API}/stop`, stopSwarm)
);

describe('StopButton', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    stopSwarm.mockClear();
  });
  afterAll(() => server.close());

  test('should stop run on StopButton click', async () => {
    const { getByText, queryByText } = renderWithProvider(<StopButton />);

    expect(queryByText('Loading')).toBeFalsy();

    act(() => {
      fireEvent.click(getByText('Stop'));
    });

    expect(getByText('Loading')).toBeTruthy();
    await waitFor(async () => {
      expect(stopSwarm).toHaveBeenCalled();
    })
  });
});
