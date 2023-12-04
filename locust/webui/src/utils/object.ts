export const objectLength = <T extends Record<string, any> | any[]>(object: T) =>
  Array.isArray(object) ? object.length : Object.keys(object).length;

export const isEmpty = <T extends Record<string, any> | any[]>(object: T) =>
  objectLength(object) === 0;

export function shallowMerge<ObjectA, ObjectB>(objectA: ObjectA, objectB: ObjectB) {
  return {
    ...objectA,
    ...objectB,
  };
}

export const createFormData = (inputData: { [key: string]: string | string[] }) => {
  const formData = new URLSearchParams();

  for (const [key, value] of Object.entries(inputData)) {
    if (Array.isArray(value)) {
      for (const element of value) {
        formData.append(key, element);
      }
    } else {
      formData.append(key, value);
    }
  }

  return formData;
};

export const updateArraysAtProps = <T extends Record<string, any>>(
  objectToUpdate: T,
  propsWithUpdates: { [K in keyof T]: T[K] extends Array<infer U> ? U : T },
) =>
  Object.entries(propsWithUpdates).reduce(
    (updatedObject, [updateProp, updateValue]) => ({
      ...updatedObject,
      [updateProp]: [...(updatedObject[updateProp] || []), updateValue],
    }),
    objectToUpdate,
  );
