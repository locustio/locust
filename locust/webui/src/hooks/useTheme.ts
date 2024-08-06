import { useMemo } from 'react';

import { THEME_MODE } from 'constants/theme';
import { useSelector } from 'redux/hooks';
import createTheme from 'styles/theme';

export default function useTheme() {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  const theme = useMemo(
    () => createTheme(isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT),
    [isDarkMode],
  );

  return theme;
}
