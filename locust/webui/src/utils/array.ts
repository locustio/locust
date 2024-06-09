export const flatten = <T>(array: any[]): T[] =>
  array.reduce(
    (flat, toFlatten) => flat.concat(Array.isArray(toFlatten) ? flatten<T>(toFlatten) : toFlatten),
    [] as T[],
  );
