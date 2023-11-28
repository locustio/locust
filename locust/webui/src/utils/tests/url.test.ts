import { afterEach, test, describe, expect } from 'vitest';

import { getUrlParams, pushQuery } from 'utils/url';

describe('pushQuery', () => {
  afterEach(() => {
    // Reset query params after each test
    window.history.pushState(null, '', window.location.pathname);
  });

  test('should push a single key-value pair to the query', () => {
    pushQuery({ param: 'value' });

    expect(window.location.search).toBe('?param=value');
  });

  test('should push multiple key-value pairs to the query', () => {
    pushQuery({ param1: 'value1', param2: 'value2', param3: 'value3' });

    expect(window.location.search).toBe('?param1=value1&param2=value2&param3=value3');
  });

  test('should overwrite existing query parameters', () => {
    pushQuery({ param1: 'firstValue', param2: 'value2' });
    pushQuery({ param1: 'newValue' });

    expect(window.location.search).toBe('?param1=newValue&param2=value2');
  });
});

describe('getUrlParams', () => {
  test('should return null when there are no query parameters', () => {
    const params = getUrlParams();

    expect(params).toBeNull();
  });

  test('should return an object with query parameters', () => {
    const params = { param1: 'value1', param2: 'value2' };
    pushQuery(params);

    expect(params).toEqual(getUrlParams());
  });
});
