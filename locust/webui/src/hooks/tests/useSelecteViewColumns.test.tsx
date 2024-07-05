import { act, renderHook } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import useSelectViewColumns from 'hooks/useSelectViewColumns';

const mockStructure = [
  { title: 'Method', key: 'method' },
  { title: 'Name', key: 'name' },
  { title: '# Requests', key: 'numRequests' },
];

const mockStats = [
  {
    avgContentLength: 200,
    avgResponseTime: 150,
    currentFailPerSec: 0.5,
    currentRps: 20,
    maxResponseTime: 300,
    overThresholdCount: 10,
    medianResponseTime: 140,
    method: 'GET' as const,
    minResponseTime: 100,
    name: 'Endpoint 1',
    numFailures: 5,
    numRequests: 100,
    safeName: 'Endpoint_1',
    responseTimePercentile50: 140,
    responseTimePercentile75: 180,
    responseTimePercentile90: 220,
    responseTimePercentile95: 250,
    responseTimePercentile99: 290,
  },
  {
    avgContentLength: 300,
    avgResponseTime: 250,
    currentFailPerSec: 0.8,
    currentRps: 15,
    maxResponseTime: 400,
    overThresholdCount: 12,
    medianResponseTime: 240,
    method: 'POST' as const,
    minResponseTime: 200,
    name: 'Endpoint 2',
    numFailures: 8,
    numRequests: 200,
    safeName: 'Endpoint_2',
    responseTimePercentile50: 240,
    responseTimePercentile75: 280,
    responseTimePercentile90: 320,
    responseTimePercentile95: 350,
    responseTimePercentile99: 390,
  },
];

describe('useSelectViewColumns hook', () => {
  test('should initialize with default columns', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure, mockStats));

    expect(result.current.selectedColumns).toEqual(mockStructure.map(s => s.key));
  });

  test('should add a new column', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure, mockStats));

    act(() => {
      result.current.addColumn('column3');
    });

    expect(result.current.selectedColumns).toEqual([...mockStructure.map(s => s.key), 'column3']);
  });

  test('should remove an existing column', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure, mockStats));

    act(() => {
      result.current.removeColumn('method');
    });

    expect(result.current.selectedColumns).toEqual(['name', 'numRequests']);
  });

  test('filterStructure should filter out unselected columns', () => {
    const { result } = renderHook(() => useSelectViewColumns(mockStructure, mockStats));

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
