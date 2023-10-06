import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface IThemeState {
  isDarkMode: boolean;
}

export type ThemeAction = PayloadAction<boolean>;

const initialState = {
  isDarkMode: false,
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setIsDarkMode: (state, { payload }) => {
      state.isDarkMode = payload;
    },
  },
});

export const themeActions = themeSlice.actions;
export default themeSlice.reducer;
