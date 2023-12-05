import { test, describe, expect } from 'vitest';

import {
  createFormData,
  isEmpty,
  objectLength,
  shallowMerge,
  updateArraysAtProps,
} from 'utils/object';

describe('objectLength', () => {
  test('should return 0 for an empty object', () => {
    expect(objectLength({})).toBe(0);
  });

  test('should return correct length for an object with properties', () => {
    expect(objectLength({ key: 'value' })).toBe(1);
    expect(objectLength({ key: 'value', key2: 'value2', key3: 'value3' })).toBe(3);
  });

  test('should return 0 for an empty array', () => {
    expect(objectLength([])).toBe(0);
  });

  test('should return correct length for an array with elements', () => {
    expect(objectLength([1])).toBe(1);
    expect(objectLength([1, 2, 3])).toBe(3);
  });
});

describe('isEmpty', () => {
  test('should return true for an empty object', () => {
    expect(isEmpty({})).toBeTruthy();
  });

  test('should return false for an object with properties', () => {
    expect(isEmpty({ key: 'value' })).toBeFalsy();
  });

  test('should return true for an empty array', () => {
    expect(isEmpty([])).toBeTruthy();
  });

  test('should return false for an array with elements', () => {
    expect(isEmpty([1, 2, 3])).toBeFalsy();
  });
});

describe('shallowMerge', () => {
  test('should merge two empty objects', () => {
    expect(shallowMerge({}, {})).toEqual({});
  });

  test('should merge two objects with different properties', () => {
    const objectA = { a: 1, b: 'hello' };
    const objectB = { c: true, d: [1, 2, 3] };

    expect(shallowMerge(objectA, objectB)).toEqual({ a: 1, b: 'hello', c: true, d: [1, 2, 3] });
  });

  test('should overwrite properties from objectA with those from objectB', () => {
    const objectA = { a: 1, b: 'hello', c: true };
    const objectB = { b: 'world', d: [4, 5, 6] };

    expect(shallowMerge(objectA, objectB)).toEqual({ a: 1, b: 'world', c: true, d: [4, 5, 6] });
  });

  test('should not modify original objects', () => {
    const objectA = { a: 1, b: 'hello' };
    const objectB = { c: true, d: [1, 2, 3] };

    shallowMerge(objectA, objectB);

    expect(objectA).toEqual({ a: 1, b: 'hello' });
    expect(objectB).toEqual({ c: true, d: [1, 2, 3] });
  });
});

describe('createFormData', () => {
  test('should create FormData from an empty object', () => {
    const formData = createFormData({});
    expect(formData.toString()).toEqual('');
  });

  test('should create FormData from an object with string values', () => {
    const inputData = { method: 'GET', numRequests: '25' };
    const formData = createFormData(inputData);

    expect(formData.toString()).toEqual('method=GET&numRequests=25');
  });

  test('should create FormData from an object with array values', () => {
    const inputData = { tasks: ['task1', 'task2', 'task3'], stats: ['1', '2', '3'] };
    const formData = createFormData(inputData);

    expect(formData.toString()).toEqual(
      'tasks=task1&tasks=task2&tasks=task3&stats=1&stats=2&stats=3',
    );
  });
});

describe('updateArraysAtProps', () => {
  test('should update arrays at specified properties', () => {
    const originalObject = {
      time: ['10:10:10', '20:20:20'],
      rps: [25, 30],
    };

    const updatedProps = {
      time: '30:30:30',
      rps: 35,
    };

    const updatedObject = updateArraysAtProps(originalObject, updatedProps);

    expect(updatedObject.time).toEqual(['10:10:10', '20:20:20', '30:30:30']);
    expect(updatedObject.rps).toEqual([25, 30, 35]);
  });

  test('should handle properties that are not present in the original object', () => {
    const originalObject = {
      time: ['10:10:10', '20:20:20'],
      rps: [25, 30],
    };

    const updatedProps = {
      time: '30:30:30',
      rps: 35,
      markers: 10,
    };

    const updatedObject = updateArraysAtProps(originalObject, updatedProps) as {
      time: string[];
      rps: number[];
      markers: number[];
    };

    expect(updatedObject.time).toEqual(['10:10:10', '20:20:20', '30:30:30']);
    expect(updatedObject.rps).toEqual([25, 30, 35]);
    expect(updatedObject.markers).toEqual([10]);
  });
});
