import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { connect } from 'react-redux';

import Layout from 'components/Layout/Layout';
import useLogViewer from 'components/LogViewer/useLogViewer';
import SwarmForm from 'components/SwarmForm/SwarmForm';
import Tabs from 'components/Tabs/Tabs';
import { SWARM_STATE } from 'constants/swarm';
import useCreateTheme from 'hooks/useCreateTheme';
import useFetchStats from 'hooks/useFetchStats';
import useFetchWorkerCount from 'hooks/useFetchWorkerCount';
import { IRootState } from 'redux/store';
import { ITab } from 'types/tab.types';
import { SwarmState } from 'types/ui.types';

interface IDashboard {
  isModalOpen?: boolean;
  swarmState: SwarmState;
  showTestTab: boolean;
  extendedTabs?: ITab[];
  tabs?: ITab[];
}

function Dashboard({ swarmState, showTestTab, tabs, extendedTabs }: IDashboard) {
  useFetchStats();
  useFetchWorkerCount();
  useLogViewer();

  const theme = useCreateTheme();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        {swarmState === SWARM_STATE.READY && !showTestTab ? (
          <SwarmForm />
        ) : (
          <Tabs extendedTabs={extendedTabs} tabs={tabs} />
        )}
      </Layout>
    </ThemeProvider>
  );
}

const storeConnector = ({ swarm: { state }, ui: { showTestTab } }: IRootState) => ({
  swarmState: state,
  showTestTab,
});

export default connect(storeConnector)(Dashboard);
