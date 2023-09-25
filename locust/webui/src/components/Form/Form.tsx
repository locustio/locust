import { FormEvent, useCallback } from 'react';

export type BaseInputData = Record<string, any>;

interface IForm<IInputData extends BaseInputData> {
  children: React.ReactElement | React.ReactElement[];
  className?: string;
  onSubmit: (inputData: IInputData) => void;
}

export default function Form<IInputData extends BaseInputData>({
  children,
  onSubmit,
}: IForm<IInputData>) {
  const formSubmitHandler = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const formData = new FormData(event.target as HTMLFormElement);
      const inputData: IInputData = {} as IInputData;

      for (const [key, value] of formData.entries()) {
        if (inputData.hasOwnProperty(key)) {
          if (!Array.isArray(inputData[key])) {
            (inputData[key as keyof IInputData] as unknown) = [inputData[key]];
          }

          (inputData[key] as string[]).push(value as string);
        } else {
          inputData[key as keyof IInputData] = value as IInputData[keyof IInputData];
        }
      }

      onSubmit(inputData);
    },
    [onSubmit],
  );

  return <form onSubmit={formSubmitHandler}>{children}</form>;
}
