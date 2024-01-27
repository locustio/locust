import { useState } from 'react';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import { Box, Tabs as MuiTabs, Tab as MuiTab, Container } from '@mui/material';
import { connect } from 'react-redux';

import DataTable from 'components/DataTable/DataTable';
import { baseTabs, conditionalTabs } from 'components/Tabs/Tabs.constants';
import { INotificationState, notificationActions } from 'redux/slice/notification.slice';
import { IUrlState, urlActions } from 'redux/slice/url.slice';
import { IRootState } from 'redux/store';
import { ITab } from 'types/tab.types';
import { pushQuery } from 'utils/url';

interface ITabs {
  currentTabIndexFromQuery: number;
  notification: INotificationState;
  setNotification: (payload: INotificationState) => void;
  setUrl: (payload: IUrlState) => void;
  tabs: ITab[];
}

interface ITabLabel {
  hasNotification?: boolean;
  title: string;
}

function TabLabel({ hasNotification, title }: ITabLabel) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      {hasNotification && <PriorityHighIcon color='secondary' />}
      <span>{title}</span>
    </Box>
  );
}

function Tabs({ currentTabIndexFromQuery, notification, setNotification, setUrl, tabs }: ITabs) {
  const [currentTabIndex, setCurrentTabIndex] = useState(currentTabIndexFromQuery);

  const onTabChange = (_: React.SyntheticEvent, index: number) => {
    const tab = tabs[index].key;

    if (notification[tab]) {
      setNotification({ [tab]: false });
    }

    pushQuery({ tab });
    setUrl({ query: { tab } });
    setCurrentTabIndex(index);
  };

  return (
    <Container maxWidth='xl'>
      <Box sx={{ mb: 2 }}>
        <MuiTabs onChange={onTabChange} value={currentTabIndex}>
          {tabs.map(({ key: tabKey, title }, index) => (
            <MuiTab
              key={`tab-${index}`}
              label={<TabLabel hasNotification={notification[tabKey]} title={title} />}
            />
          ))}
        </MuiTabs>
      </Box>
      {tabs.map(
        ({ component: Component = DataTable }, index) =>
          currentTabIndex === index && <Component key={`tabpabel-${index}`} />,
      )}
    </Container>
  );
}

const storeConnector = (state: IRootState) => {
  const {
    notification,
    swarm: { extendedTabs = [] },
    url: { query: urlQuery },
  } = state;

  const conditionalTabsToDisplay = conditionalTabs.filter(({ shouldDisplayTab }) =>
    shouldDisplayTab(state),
  );

  const tabs = [...baseTabs, ...conditionalTabsToDisplay, ...extendedTabs];

  return {
    notification,
    tabs,
    currentTabIndexFromQuery:
      urlQuery && urlQuery.tab ? tabs.findIndex(({ key }) => key === urlQuery.tab) : 0,
  };
};

const actionCreator = {
  setNotification: notificationActions.setNotification,
  setUrl: urlActions.setUrl,
};

export default connect(storeConnector, actionCreator)(Tabs);
