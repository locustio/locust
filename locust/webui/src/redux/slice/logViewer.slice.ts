import { PayloadAction, createSlice } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';
import { ILogsResponse } from 'types/ui.types';

export interface ILogViewerState extends ILogsResponse {}

export type LogViewerAction = PayloadAction<ILogViewerState>;

const initialState = {
  master: [] as string[],
  workers: {},
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
