type MutationFunction = (string: string) => string;

function transformValueKeys<ObjectInterface>(
  object: ObjectInterface,
  value: ObjectInterface[keyof ObjectInterface],
  mutation: MutationFunction,
) {
  if (!value) {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((n): string => transformValueKeys(object, n, mutation) as string);
  }
  if (typeof value === 'object') {
    return transformKeys(value, mutation);
  }
  return value;
}

const transformKeys = <ObjectInterface extends Record<string, any>>(
  object: ObjectInterface,
  mutation: MutationFunction,
): ObjectInterface =>
  Object.entries(object).reduce(
    (transformedObject, [key, value]) => ({
      ...transformedObject,
      [mutation(key)]: transformValueKeys<ObjectInterface>(object, value, mutation),
    }),
    {},
  ) as ObjectInterface;

export const snakeToCamelCase = (string: string) =>
  string.replace(/_([a-z0-9])/g, (_, match) => match.toUpperCase());
const camelToSnakeCase = (string: string) =>
  string[0] === string[0].toUpperCase()
    ? string
    : string.replace(/([a-z0-9])([A-Z0-9])/g, '$1_$2').toLowerCase();

export const camelCaseKeys = <ObjectInterface extends Record<string, any>>(
  object: ObjectInterface,
) => transformKeys<ObjectInterface>(object, snakeToCamelCase);
export const snakeCaseKeys = <ObjectInterface extends Record<string, any>>(
  object: ObjectInterface,
) => transformKeys<ObjectInterface>(object, camelToSnakeCase);

export const toTitleCase = (string: string) =>
  string.replace(/([a-z0-9])([A-Z0-9])/g, '$1 $2').replace(/^./, str => str.toUpperCase());

export const queryStringToObject = (queryString: string) =>
  Object.fromEntries(new URLSearchParams(queryString).entries());

export const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  if (bytes === 0) return 'N/A';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};
