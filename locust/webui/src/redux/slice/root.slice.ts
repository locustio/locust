import { combineReducers, PayloadAction } from '@reduxjs/toolkit';

import { api } from 'redux/api/swarm';
import logViewer, { ILogViewerState, LogViewerAction } from 'redux/slice/logViewer.slice';
import notification, {
  INotificationState,
  NotificationAction,
} from 'redux/slice/notification.slice';
import swarm, { ISwarmState, SwarmAction } from 'redux/slice/swarm.slice';
import theme, { IThemeState, ThemeAction } from 'redux/slice/theme.slice';
import ui, { IUiState, UiAction } from 'redux/slice/ui.slice';
import url, { IUrlState, UrlAction } from 'redux/slice/url.slice';

export interface IRootState {
  logViewer: ILogViewerState;
  notification: INotificationState;
  swarm: ISwarmState;
  theme: IThemeState;
  ui: IUiState;
  url: IUrlState;
}

export type Action =
  | LogViewerAction
  | NotificationAction
  | SwarmAction
  | ThemeAction
  | UiAction
  | UrlAction
  | PayloadAction<undefined>;

const rootReducer = combineReducers({
  [api.reducerPath]: api.reducer,
  logViewer,
  notification,
  swarm,
  theme,
  ui,
  url,
});

export default rootReducer;
