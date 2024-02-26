import { ISwarmState } from 'redux/slice/swarm.slice';
import { IReport, IReportTemplateArgs } from 'types/swarm.types';
import { ICharts } from 'types/ui.types';
import { updateArraysAtProps } from 'utils/object';
import { camelCaseKeys } from 'utils/string';

export const SWARM_STATE = {
  READY: 'ready',
  RUNNING: 'running',
  STOPPED: 'stopped',
  SPAWNING: 'spawning',
  CLEANUP: 'cleanup',
  STOPPING: 'stopping',
  MISSING: 'missing',
};

export const swarmTemplateArgs = window.templateArgs
  ? camelCaseKeys(window.templateArgs)
  : ({} as ISwarmState | IReportTemplateArgs);

export const htmlReportProps: IReport | false = !!(swarmTemplateArgs as IReportTemplateArgs)
  .isReport && {
  ...(swarmTemplateArgs as IReportTemplateArgs),
  charts: swarmTemplateArgs.history?.reduce(
    (charts, { currentResponseTimePercentiles, ...history }) =>
      updateArraysAtProps(charts, { ...currentResponseTimePercentiles, ...history }),
    {} as ICharts,
  ) as ICharts,
};
