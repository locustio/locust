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
    const { result } = renderHook(() => useSelectViewColumns(mockStructure));

    expect(result.current.selectedColumns).toEqual(mockStructure.map(s => s.key));
  });

  test('should add a new column', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure));

    act(() => {
      result.current.addColumn('column3');
    });

    expect(result.current.selectedColumns).toEqual([...mockStructure.map(s => s.key), 'column3']);
  });

  test('should remove an existing column', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure));

    act(() => {
      result.current.removeColumn('method');
    });

    expect(result.current.selectedColumns).toEqual(['name', 'numRequests']);
  });

  test('filterStructure should filter out unselected columns', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure));

    act(() => {
      // remove column with key 'method'
      result.current.removeColumn('method');
    });

    const filteredStructure = result.current.filteredStructure;

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
