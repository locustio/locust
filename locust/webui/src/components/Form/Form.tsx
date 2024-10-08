import { FormEvent, useCallback } from 'react';

export type BaseInputData = Record<string, any>;

interface IForm<IInputData extends BaseInputData> {
  children: React.ReactElement | React.ReactElement[];
  className?: string;
  onSubmit: (inputData: IInputData) => void;
  onChange?: (formEvent: React.ChangeEvent<HTMLFormElement>) => void;
}

const FORM_INPUT_ELEMENTS = 'input, select, textarea';

const getInputValue = (inputElement: HTMLInputElement | HTMLSelectElement) => {
  if (
    inputElement instanceof HTMLInputElement &&
    inputElement.getAttribute('data-type') === 'number'
  ) {
    return Number(inputElement.value);
  }

  if (inputElement instanceof HTMLInputElement && inputElement.type === 'checkbox') {
    return inputElement.checked;
  }

  if (inputElement instanceof HTMLSelectElement && inputElement.multiple) {
    return Array.from(inputElement.selectedOptions).map(option => option.value);
  }

  return inputElement.value;
};

export default function Form<IInputData extends BaseInputData>({
  children,
  onSubmit,
  onChange,
}: IForm<IInputData>) {
  const formSubmitHandler = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const form = event.target as HTMLFormElement;
      const inputData: IInputData = [
        ...form.querySelectorAll<HTMLInputElement | HTMLSelectElement>(FORM_INPUT_ELEMENTS),
      ].reduce(
        (inputData, inputElement) => ({
          ...inputData,
          [inputElement.name]: getInputValue(inputElement),
        }),
        {} as IInputData,
      );

      onSubmit(inputData);
    },
    [onSubmit],
  );

  return (
    <form onChange={onChange} onSubmit={formSubmitHandler}>
      {children}
    </form>
  );
}
