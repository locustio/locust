export interface ICustomInput {
  label: string;
  name: string;
  type?: string;
  choices?: string[] | null;
  isMultiple?: boolean;
  defaultValue?: string | number | boolean | null;
  isSecret?: boolean;
  isRequired?: boolean;
}
