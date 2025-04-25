import { act, fireEvent, waitFor } from '@testing-library/react';
import { http } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterAll, describe, test, expect, vi, afterEach } from 'vitest';

import ResetButton from 'components/StateButtons/ResetButton';
import { TEST_BASE_API } from 'test/constants';
import { renderWithProvider } from 'test/testUtils';

const resetStats = vi.fn();

const server = setupServer(
  http.get(`${TEST_BASE_API}/stats/reset`, resetStats,
  ),
);


describe('ResetButton', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    resetStats.mockClear();
  });
  afterAll(() => server.close());

  test('should call resetStats on ResetButton click', async () => {
    const { getByText } = renderWithProvider(<ResetButton />);

    act(() => {
      fireEvent.click(getByText('Reset'));
    });

    await waitFor(async () => {
      expect(resetStats).toHaveBeenCalled();
    })
  });
});
