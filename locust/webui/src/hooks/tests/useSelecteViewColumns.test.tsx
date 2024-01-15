import { act, renderHook } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import useSelectViewColumns from 'hooks/useSelectViewColumns';

const mockStructure = [
  { title: 'Method', key: 'method' },
  { title: 'Name', key: 'name' },
  { title: '# Requests', key: 'numRequests' },
];

describe('useSelectViewColumns hook', () => {
  test('should initialize with default columns', () => {
    const defaultColumns = ['column1', 'column2'];
    const { result } = renderHook(() => useSelectViewColumns(defaultColumns));

    expect(result.current.selectedColumns).toEqual(defaultColumns);
  });

  test('should add a new column', () => {
    const defaultColumns = ['column1', 'column2'];
    const { result } = renderHook(() => useSelectViewColumns(defaultColumns));

    act(() => {
      result.current.addColumn('column3');
    });

    expect(result.current.selectedColumns).toEqual([...defaultColumns, 'column3']);
  });

  test('should remove an existing column', () => {
    const defaultColumns = ['column1', 'column2'];
    const { result } = renderHook(() => useSelectViewColumns(defaultColumns));

    act(() => {
      result.current.removeColumn('column1');
    });

    expect(result.current.selectedColumns).toEqual(['column2']);
  });

  test('filterStructure should filter out unselected columns', () => {
    const defaultColumns = mockStructure.map(({ key }) => key);

    const { result } = renderHook(() => useSelectViewColumns(defaultColumns));

    act(() => {
      // remove column with key 'method'
      result.current.removeColumn('method');
    });

    const filteredStructure = result.current.filterStructure(mockStructure);

    // expect only columns with keys 'name' and 'numRequests' to be returned
    expect(filteredStructure.length).toBe(2);
    expect(filteredStructure).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ key: 'name' }),
        expect.objectContaining({ key: 'numRequests' }),
      ]),
    );
    expect(filteredStructure).not.toContainEqual(expect.objectContaining({ key: 'method' }));
  });
});
