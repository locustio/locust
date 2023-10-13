import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';
import { IExtraOptions, History } from 'types/swarm.types';
import { ITab } from 'types/tab.types';
import { ITableStructure } from 'types/table.types';
import { camelCaseKeys } from 'utils/string';

export interface ISwarmState {
  auth: {
    email: string;
    name: string;
  };
  availableShapeClasses: string[];
  availableUserClasses: string[];
  extraOptions: IExtraOptions;
  extendedTabs?: ITab[];
  extendedTables?: { key: string; structure: ITableStructure[] }[];
  extendedCsvFiles?: { href: string; title: string }[];
  hasMultipleHosts: boolean;
  history: History[];
  host: string | string[];
  isDistributed: boolean;
  isShape: boolean | null;
  locustfile: string;
  numUsers: number | null;
  overrideHostWarning: boolean;
  runTime: number;
  showUserclassPicker: boolean;
  spawnRate: number | null;
  state: string;
  statsHistoryEnabled: boolean;
  tasks: string;
  userCount: number | string;
  version: string;
  workerCount: number;
}

export type SwarmAction = PayloadAction<Partial<ISwarmState>>;

const initialState = camelCaseKeys(window.templateArgs) as ISwarmState;

const swarmSlice = createSlice({
  name: 'swarm',
  initialState,
  reducers: {
    setSwarm: updateStateWithPayload<ISwarmState, SwarmAction>,
  },
});

export const swarmActions = swarmSlice.actions;
export default swarmSlice.reducer;
