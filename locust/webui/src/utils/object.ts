export const isEmpty = <T extends Record<string, any> | any[]>(object: T) =>
  (Array.isArray(object) ? object.length : Object.keys(object).length) === 0;

export function shallowMerge<ObjectA, ObjectB>(objectA: ObjectA, objectB: ObjectB) {
  return {
    ...objectA,
    ...objectB,
  };
}

export const createFormData = <
  IInputdata extends Record<string, any> = { [key: string]: string | string[] },
>(
  inputData: IInputdata,
) => {
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
