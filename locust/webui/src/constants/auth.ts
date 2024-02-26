import { IAuthArgs } from 'types/auth.types';
import { camelCaseKeys } from 'utils/string';

export const authArgs: IAuthArgs | false = !!window.authArgs && camelCaseKeys(window.authArgs);
