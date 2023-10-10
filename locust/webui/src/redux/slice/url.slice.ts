import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { updateStateWithPayload } from 'redux/utils';
import { getUrlParams } from 'utils/url';

export interface IUrlState {
  query: { [key: string]: string } | null;
}

export type UrlAction = PayloadAction<Partial<IUrlState>>;

const initialState = {
  query: getUrlParams(),
};

const urlSlice = createSlice({
  name: 'url',
  initialState,
  reducers: {
    setUrl: updateStateWithPayload<IUrlState, UrlAction>,
  },
});

export const urlActions = urlSlice.actions;
export default urlSlice.reducer;
