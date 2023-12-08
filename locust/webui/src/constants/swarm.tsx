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

export const swarmTemplateArgs = camelCaseKeys(window.templateArgs);
