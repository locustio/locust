import { combineReducers, PayloadAction } from '@reduxjs/toolkit';

import swarm, { ISwarmState, SwarmAction } from 'redux/slice/swarm.slice';
import theme, { IThemeState, ThemeAction } from 'redux/slice/theme.slice';
import ui, { IUiState, UiAction } from 'redux/slice/ui.slice';
import url, { IUrlState, UrlAction } from 'redux/slice/url.slice';

export interface IRootState {
  swarm: ISwarmState;
  theme: IThemeState;
  ui: IUiState;
  url: IUrlState;
}

export type Action = SwarmAction | ThemeAction | UiAction | UrlAction | PayloadAction<undefined>;

const rootReducer = combineReducers({ swarm, theme, ui, url });

export default rootReducer;
