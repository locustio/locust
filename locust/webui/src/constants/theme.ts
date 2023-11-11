import { PaletteMode } from '@mui/material';

export const THEME_MODE: { [key: string]: PaletteMode } = {
  DARK: 'dark',
  LIGHT: 'light',
};

export const INITIAL_THEME =
  localStorage.theme === THEME_MODE.DARK ||
  (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
    ? THEME_MODE.DARK
    : THEME_MODE.LIGHT;
