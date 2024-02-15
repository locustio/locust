import { PaletteMode, createTheme as baseCreateTheme } from '@mui/material';

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
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          ':root': {
            '--footer-height': '40px',
          },
        },
      },
    },
  });

export default createTheme;
