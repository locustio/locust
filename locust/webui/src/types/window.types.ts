import { PaletteMode } from '@mui/material';

import type { ISwarmState } from 'redux/slice/swarm.slice';
import { IAuthArgs } from 'types/auth.types';
import { IReportTemplateArgs } from 'types/swarm.types';

export interface IWindow {
  templateArgs: IReportTemplateArgs | ISwarmState;
  authArgs: IAuthArgs;
  theme?: PaletteMode;
}
