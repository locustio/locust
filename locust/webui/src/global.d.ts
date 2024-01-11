import { PaletteMode } from '@mui/material';

import type { ISwarmState } from 'redux/slice/swarm.slice';
import { IAuthArgs } from 'types/auth.types';
import { IReportTemplateArgs } from 'types/swarm.types';

declare global {
  interface Window {
    templateArgs: IReportTemplateArgs | ISwarmState;
    authArgs: IAuthArgs;
    theme?: PaletteMode;
  }
}
