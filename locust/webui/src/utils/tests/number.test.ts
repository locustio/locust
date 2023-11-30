import { test, describe, expect } from 'vitest';

import { roundToDecimalPlaces } from 'utils/number';

describe('roundToDecimalPlaces', () => {
  test('should round to 0 decimal places by default', () => {
    expect(roundToDecimalPlaces(3.14159)).toBe(3);
  });

  test('should round to the specified number of decimal places', () => {
    expect(roundToDecimalPlaces(3.14159, 2)).toBe(3.14);
  });
});
