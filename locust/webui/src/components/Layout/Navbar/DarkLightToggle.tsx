import { useEffect } from 'react';
import DarkModeIcon from '@mui/icons-material/Brightness4';
import LightModeIcon from '@mui/icons-material/Brightness7';
import { IconButton } from '@mui/material';

import { INITIAL_THEME, THEME_MODE } from 'constants/theme';
import { useAction, useSelector } from 'redux/hooks';
import { themeActions } from 'redux/slice/theme.slice';

export default function DarkLightToggle() {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);
  const setIsDarkMode = useAction(themeActions.setIsDarkMode);

  useEffect(() => {
    // set dark mode based on local storage
    // or users browser preferences
    setIsDarkMode(INITIAL_THEME === THEME_MODE.DARK);
  }, []);

  const toggleMode = () => {
    localStorage.theme = !isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT;
    setIsDarkMode(!isDarkMode);
  };

  return (
    <IconButton color='inherit' onClick={toggleMode}>
      {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
    </IconButton>
  );
}
