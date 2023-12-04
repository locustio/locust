import { PayloadAction, createSlice } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';

export interface ILogViewerState {
  logs: string[];
}

export type LogViewerAction = PayloadAction<ILogViewerState>;

const initialState = {
  logs: [] as string[],
};

const logViewerSlice = createSlice({
  name: 'logViewer',
  initialState,
  reducers: {
    setLogs: updateStateWithPayload<ILogViewerState, LogViewerAction>,
  },
});

export const logViewerActions = logViewerSlice.actions;
export default logViewerSlice.reducer;
