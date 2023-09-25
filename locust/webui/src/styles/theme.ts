import { PaletteMode, createTheme as baseCreateTheme } from '@mui/material';

export const THEME_MODE: { [key: string]: PaletteMode } = {
  DARK: 'dark',
  LIGHT: 'light',
};

const createTheme = (mode: PaletteMode) =>
  baseCreateTheme({
    palette: {
      mode,
      primary: {
        main: '#15803d',
      },
      success: {
        main: '#00C853',
      },
    },
  });

export default createTheme;
