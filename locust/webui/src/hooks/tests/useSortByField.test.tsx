import { act, render } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import useSortByField from 'hooks/useSortByField';

const mockStats = [
  { name: '/test1', method: 'GET', numRequests: 6, numFailures: 11 },
  { name: '/test2', method: 'POST', numRequests: 22, numFailures: 43 },
  { name: '/test3', method: 'GET', numRequests: 44, numFailures: 0 },
];

const mockStatsWithTotalRow = [
  ...mockStats,
  { name: 'Aggregated', method: '', numRequests: 72, numFailures: 15 },
];

function MockHook({
  hasTotalRow,
  defaultSortKey,
}: {
  hasTotalRow?: boolean;
  defaultSortKey?: keyof (typeof mockStats)[0];
}) {
  const { onTableHeadClick, sortedRows, currentSortField } = useSortByField(
    hasTotalRow ? mockStatsWithTotalRow : mockStats,
    {
      hasTotalRow,
      defaultSortKey,
    },
  );

  return (
    <div>
      <button
        data-sortkey='numRequests'
        data-testid='sortedByNumRequests'
        onClick={onTableHeadClick}
      >
        Sort by numRequests
      </button>
      <button
        data-sortkey='numFailures'
        data-testid='sortedByNumFailures'
        onClick={onTableHeadClick}
      >
        Sort by numFailures
      </button>
      <span data-testid='sortedStats'>{JSON.stringify(sortedRows)}</span>
      <span data-testid='currentSortField'>{currentSortField}</span>
    </div>
  );
}

describe('useSortByField', () => {
  test('should sort stats by defaultSortKey', () => {
    const { getByTestId } = render(<MockHook />);

    expect(getByTestId('sortedStats').textContent).toBe(JSON.stringify(mockStats));
  });

  test('should allow defaultSortKey to be overriden', () => {
    const { getByTestId } = render(<MockHook defaultSortKey='method' />);

    expect(getByTestId('sortedStats').textContent).toBe(
      JSON.stringify([mockStats[0], mockStats[2], mockStats[1]]),
    );
  });

  test('should retain the total row at the tail of the stats', () => {
    const { getByTestId } = render(<MockHook hasTotalRow />);

    expect(getByTestId('sortedStats').textContent).toBe(JSON.stringify(mockStatsWithTotalRow));
  });

  test('should have the initial currentSortField set as empty', () => {
    const { getByTestId } = render(<MockHook />);

    expect(getByTestId('currentSortField').textContent).toBe('');
  });

  test('should update the currentSortField and sort the stats by specified sortKey', () => {
    const { getByTestId } = render(<MockHook />);

    act(() => {
      getByTestId('sortedByNumRequests').click();
    });

    expect(getByTestId('sortedStats').textContent).toBe(
      JSON.stringify([mockStats[0], mockStats[1], mockStats[2]]),
    );

    act(() => {
      getByTestId('sortedByNumFailures').click();
    });

    expect(getByTestId('sortedStats').textContent).toBe(
      JSON.stringify([mockStats[2], mockStats[0], mockStats[1]]),
    );
  });

  test('should sort the stats in reverse on 2nd click', () => {
    const { getByTestId } = render(<MockHook />);

    act(() => {
      getByTestId('sortedByNumRequests').click();
      getByTestId('sortedByNumRequests').click();
    });

    expect(getByTestId('sortedStats').textContent).toBe(
      JSON.stringify([mockStats[2], mockStats[1], mockStats[0]]),
    );
    expect(getByTestId('currentSortField').textContent).toBe('numRequests');
  });

  test('should clear the currentSortField and sort the stats by defaultSortKey on 3rd click', () => {
    const { getByTestId } = render(<MockHook />);

    act(() => {
      getByTestId('sortedByNumRequests').click();
      getByTestId('sortedByNumRequests').click();
    });

    act(() => {
      getByTestId('sortedByNumRequests').click();
    });

    expect(getByTestId('sortedStats').textContent).toBe(JSON.stringify(mockStats));
    expect(getByTestId('currentSortField').textContent).toBe('');
  });
});
