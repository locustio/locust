import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { swarmTemplateArgs } from 'constants/swarm';
import { updateStateWithPayload } from 'redux/utils';
import { IExtraOptions, IHistory, ISwarmUser } from 'types/swarm.types';
import { ITab } from 'types/tab.types';
import { ITableStructure } from 'types/table.types';

export interface ISwarmState {
  availableShapeClasses: string[];
  availableUserClasses: string[];
  availableUserTasks: { [key: string]: string[] };
  extraOptions: IExtraOptions;
  extendedTabs?: ITab[];
  extendedTables?: { key: string; structure: ITableStructure[] }[];
  extendedCsvFiles?: { href: string; title: string }[];
  history: IHistory[];
  host: string;
  isDistributed: boolean;
  isShape: boolean | null;
  locustfile: string;
  numUsers: number | null;
  overrideHostWarning: boolean;
  percentilesToChart: number[];
  percentilesToStatistics: number[];
  runTime?: string | number;
  showUserclassPicker: boolean;
  spawnRate: number | null;
  state: string;
  statsHistoryEnabled: boolean;
  tasks: string;
  userCount: number | string;
  users: { [key: string]: ISwarmUser };
  version: string;
  workerCount: number;
}

export type SwarmAction = PayloadAction<Partial<ISwarmState>>;

const initialState = swarmTemplateArgs as ISwarmState;

const swarmSlice = createSlice({
  name: 'swarm',
  initialState,
  reducers: {
    setSwarm: updateStateWithPayload<ISwarmState, SwarmAction>,
  },
});

export const swarmActions = swarmSlice.actions;
export default swarmSlice.reducer;
