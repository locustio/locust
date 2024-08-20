export const roundToDecimalPlaces = (n: number, decimalPlaces = 0) => {
  const factor = Math.pow(10, decimalPlaces);
  return Math.round(n * factor) / factor;
};

export const padStart = (n: number, length = 0, padding = '0') =>
  String(n).padStart(length, padding);
