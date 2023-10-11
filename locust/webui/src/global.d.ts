import { PaletteMode } from '@mui/material';

import type { ISwarmState } from 'redux/slice/swarm.slice';
import { IReportTemplateArgs } from 'types/swarm.types';

declare global {
  interface Window {
    templateArgs: IReportTemplateArgs | ISwarmState;
    theme?: PaletteMode;
  }
}
