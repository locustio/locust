import { ICustomInput } from 'types/form.types';

export interface IAuthProviders {
  label: string;
  iconUrl: string;
  callbackUrl: string;
}

export interface IAuthArgs {
  usernamePasswordCallback?: string;
  error?: string;
  info?: string;
  authProviders?: IAuthProviders[];
  customForm?: {
    inputs: ICustomInput[];
    callbackUrl: string;
    submitButtonText?: string;
  };
}
