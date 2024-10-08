import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { swarmTemplateArgs } from 'constants/swarm';
import { updateStateWithPayload } from 'redux/utils';
import { ISwarmState } from 'types/swarm.types';

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
