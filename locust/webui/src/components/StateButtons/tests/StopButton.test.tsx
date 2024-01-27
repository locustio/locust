import { act, fireEvent } from '@testing-library/react';
import { beforeAll, afterAll, describe, test, expect, vi } from 'vitest';

import StopButton from 'components/StateButtons/StopButton';
import { renderWithProvider } from 'test/testUtils';

const resetStats = vi.fn();
const baseFetch = fetch;

describe('StopButton', () => {
  beforeAll(() => {
    global.fetch = resetStats;
  });
  afterAll(() => {
    global.fetch = baseFetch;
  });

  test('should stop run on StopButton click', async () => {
    const { getByText, queryByText, rerender } = renderWithProvider(<StopButton />);

    act(() => {
      fireEvent.click(getByText('Stop'));
    });

    expect(getByText('Loading')).toBeTruthy();

    expect(resetStats).toHaveBeenCalled();
    expect(resetStats).toBeCalledWith('stop');
    rerender(<StopButton />);
    expect(queryByText('Loading')).toBeFalsy();
  });
});
