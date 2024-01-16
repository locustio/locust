export interface IAuthProviders {
  label: string;
  iconUrl: string;
  callbackUrl: string;
}

export interface IAuthArgs {
  usernamePasswordCallback?: string;
  error?: string;
  authProviders?: IAuthProviders[];
}
