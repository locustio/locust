import { act, renderHook } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import useSelectViewColumns from 'hooks/useSelectViewColumns';

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
});
