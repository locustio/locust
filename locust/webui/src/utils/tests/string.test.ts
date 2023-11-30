import { test, describe, expect } from 'vitest';

import {
  camelCaseKeys,
  formatBytes,
  queryStringToObject,
  snakeCaseKeys,
  snakeToCamelCase,
  toTitleCase,
} from 'utils/string';

describe('snakeToCamelCase', () => {
  test('should convert snake_case to camelCase', () => {
    expect(snakeToCamelCase('example_string')).toBe('exampleString');
  });

  test('should handle leading underscore', () => {
    expect(snakeToCamelCase('_example_string')).toBe('ExampleString');
  });

  test('should handle multiple underscores', () => {
    expect(snakeToCamelCase('example_string_with_multiple_underscores')).toBe(
      'exampleStringWithMultipleUnderscores',
    );
  });

  test('should handle numbers after underscores', () => {
    expect(snakeToCamelCase('example_string_with_numbers_123')).toBe('exampleStringWithNumbers123');
  });
});

describe('camelCaseKeys', () => {
  test('should transform keys from snake_case to camelCase', () => {
    const input = {
      snake_case_key: 'value',
      another_snake_key: {
        nested_snake_key: 'nested_value',
      },
      array_of_snake_keys: [
        { nested_key_one: 'nested_value_one' },
        { nested_key_two: 'nested_value_two' },
      ],
    };

    const expectedOutput = {
      snakeCaseKey: 'value',
      anotherSnakeKey: {
        nestedSnakeKey: 'nested_value',
      },
      arrayOfSnakeKeys: [
        { nestedKeyOne: 'nested_value_one' },
        { nestedKeyTwo: 'nested_value_two' },
      ],
    };

    const result = camelCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should handle empty objects and arrays', () => {
    const input = {
      empty_object: {},
      empty_array: [],
    };

    const expectedOutput = {
      emptyObject: {},
      emptyArray: [],
    };

    const result = camelCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should not transform non-snake_case keys', () => {
    const input = {
      camelCaseKey: 'value',
      PascalCaseKey: 'another_value',
      'kebab-case-key': 'yet_another_value',
    };

    const expectedOutput = {
      camelCaseKey: 'value',
      PascalCaseKey: 'another_value',
      'kebab-case-key': 'yet_another_value',
    };

    const result = camelCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should transform keys in deeply nested structures', () => {
    const input = {
      top_level_key: 'value',
      nested_structure: {
        first_level_key: 'nested_value',
        deeper_structure: {
          second_level_key: 'deep_value',
        },
      },
    };

    const expectedOutput = {
      topLevelKey: 'value',
      nestedStructure: {
        firstLevelKey: 'nested_value',
        deeperStructure: {
          secondLevelKey: 'deep_value',
        },
      },
    };

    const result = camelCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });
});

describe('snakeCaseKeys', () => {
  test('should transform keys from camelCase to snake_case', () => {
    const input = {
      camelCaseKey: 'value',
      anotherCamelKey: {
        nestedCamelKey: 'nested_value',
      },
      arrayOfCamelKeys: [
        { nestedKeyOne: 'nested_value_one' },
        { nestedKeyTwo: 'nested_value_two' },
      ],
    };

    const expectedOutput = {
      camel_case_key: 'value',
      another_camel_key: {
        nested_camel_key: 'nested_value',
      },
      array_of_camel_keys: [
        { nested_key_one: 'nested_value_one' },
        { nested_key_two: 'nested_value_two' },
      ],
    };

    const result = snakeCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should handle empty objects and arrays', () => {
    const input = {
      emptyObject: {},
      emptyArray: [],
    };

    const expectedOutput = {
      empty_object: {},
      empty_array: [],
    };

    const result = snakeCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should not transform non-camelCase keys', () => {
    const input = {
      snake_case_key: 'value',
      PascalCaseKey: 'another_value',
      'kebab-case-key': 'yet_another_value',
    };

    const expectedOutput = {
      snake_case_key: 'value',
      PascalCaseKey: 'another_value',
      'kebab-case-key': 'yet_another_value',
    };

    const result = snakeCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });

  test('should transform keys in deeply nested structures', () => {
    const input = {
      topLevelKey: 'value',
      nestedStructure: {
        firstLevelKey: 'nested_value',
        deeperStructure: {
          secondLevelKey: 'deep_value',
        },
      },
    };

    const expectedOutput = {
      top_level_key: 'value',
      nested_structure: {
        first_level_key: 'nested_value',
        deeper_structure: {
          second_level_key: 'deep_value',
        },
      },
    };

    const result = snakeCaseKeys(input);
    expect(result).toEqual(expectedOutput);
  });
});

describe('toTitleCase', () => {
  test('should convert a camelCase string to title case', () => {
    expect(toTitleCase('camelCaseString')).toEqual('Camel Case String');
  });

  test('should handle an empty string', () => {
    expect(toTitleCase('')).toEqual('');
  });

  test('should handle a single-character string', () => {
    expect(toTitleCase('a')).toEqual('A');
  });
});

describe('queryStringToObject', () => {
  test('should convert query string to object', () => {
    const queryString = '?param1=value1&param2=value2&param3=value3';

    expect(queryStringToObject(queryString)).toEqual({
      param1: 'value1',
      param2: 'value2',
      param3: 'value3',
    });
  });

  test('should handle empty query string', () => {
    expect(queryStringToObject('')).toEqual({});
  });
});

describe('formatBytes', () => {
  test('should format bytes', () => {
    const result = formatBytes(1024);
    expect(result).toBe('1 KB');
  });

  test('should handle zero bytes', () => {
    const result = formatBytes(0);
    expect(result).toBe('0 Bytes');
  });

  test('should handle large byte values', () => {
    const result = formatBytes(1e25);
    expect(result).toBe('8.27 YB');
  });
});
