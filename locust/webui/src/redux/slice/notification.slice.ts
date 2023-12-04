import { PayloadAction, createSlice } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';

export interface INotificationState {
  [key: string]: boolean;
}

export type NotificationAction = PayloadAction<INotificationState>;

const initialState = {};

const notificationSlice = createSlice({
  name: 'notification',
  initialState,
  reducers: {
    setNotification: updateStateWithPayload<INotificationState, NotificationAction>,
  },
});

export const notificationActions = notificationSlice.actions;
export default notificationSlice.reducer;
