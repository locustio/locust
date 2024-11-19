export interface ICustomInput {
  label: string;
  name: string;
  type?: string;
  choices?: string[] | null;
  defaultValue?: string | number | boolean | null;
  isSecret?: boolean;
  isRequired?: boolean;
}
