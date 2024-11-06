import { PaletteMode } from '@mui/material';

import { IAuthArgs } from 'types/auth.types';
import { IReportTemplateArgs, ISwarmState } from 'types/swarm.types';

export interface IWindow {
  templateArgs: IReportTemplateArgs | ISwarmState;
  authArgs: IAuthArgs;
  theme?: PaletteMode;
}
