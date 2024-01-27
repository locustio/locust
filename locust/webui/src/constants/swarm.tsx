import { ISwarmState } from 'redux/slice/swarm.slice';
import { IReportTemplateArgs } from 'types/swarm.types';
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
