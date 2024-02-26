import { useMemo } from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { connect } from 'react-redux';

import Layout from 'components/Layout/Layout';
import useLogViewer from 'components/LogViewer/useLogViewer';
import SwarmForm from 'components/SwarmForm/SwarmForm';
import Tabs from 'components/Tabs/Tabs';
import { SWARM_STATE } from 'constants/swarm';
import { THEME_MODE } from 'constants/theme';
import useSwarmUi from 'hooks/useSwarmUi';
import { IRootState } from 'redux/store';
import createTheme from 'styles/theme';
import { SwarmState } from 'types/ui.types';

interface IDashboard {
  isDarkMode: boolean;
  isModalOpen?: boolean;
  swarmState: SwarmState;
}

function Dashboard({ isDarkMode, swarmState }: IDashboard) {
  useSwarmUi();
  useLogViewer();

  const theme = useMemo(
    () => createTheme(isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT),
    [isDarkMode],
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>{swarmState === SWARM_STATE.READY ? <SwarmForm /> : <Tabs />}</Layout>
    </ThemeProvider>
  );
}

const storeConnector = ({ swarm: { state }, theme: { isDarkMode } }: IRootState) => ({
  isDarkMode,
  swarmState: state,
});

export default connect(storeConnector)(Dashboard);
