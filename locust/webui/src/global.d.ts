import type { ISwarmState } from 'redux/slice/swarm.slice';

declare global {
  interface Window {
    templateArgs: ISwarmState;
  }
}
