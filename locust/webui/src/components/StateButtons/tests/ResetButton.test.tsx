import { act, fireEvent } from '@testing-library/react';
import { beforeAll, afterAll, describe, test, expect, vi } from 'vitest';

import ResetButton from 'components/StateButtons/ResetButton';
import { renderWithProvider } from 'test/testUtils';

const resetStats = vi.fn();
const baseFetch = fetch;

describe('ResetButton', () => {
  beforeAll(() => {
    global.fetch = resetStats;
  });
  afterAll(() => {
    global.fetch = baseFetch;
  });

  test('should call resetStats on ResetButton click', async () => {
    const { getByText } = renderWithProvider(<ResetButton />);

    act(() => {
      fireEvent.click(getByText('Reset'));
    });

    expect(resetStats).toHaveBeenCalled();
    expect(resetStats).toBeCalledWith('stats/reset');
  });
});
