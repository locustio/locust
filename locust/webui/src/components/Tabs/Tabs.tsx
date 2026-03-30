import { useEffect, useState } from 'react';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import { Box, Tabs as MuiTabs, Tab as MuiTab, Container } from '@mui/material';
import { connect } from 'react-redux';

import DataTable from 'components/DataTable/DataTable';
import TestTab from 'components/TestTab/TestTab';
import { baseTabs } from 'components/Tabs/Tabs.constants';
import { INotificationState, notificationActions } from 'redux/slice/notification.slice';
import { IUiState, uiActions } from 'redux/slice/ui.slice';
import { IUrlState, urlActions } from 'redux/slice/url.slice';
import { IRootState } from 'redux/store';
import { ITab } from 'types/tab.types';
import { pushQuery } from 'utils/url';

interface IStateProps {
  extendedTabs?: ITab[];
  tabs?: ITab[];
}

interface ITabs extends IStateProps {
  currentTabIndexFromQuery: number;
  notification: INotificationState;
  showTestTab: boolean;
  setNotification: (payload: INotificationState) => void;
  setUi: (payload: Partial<IUiState>) => void;
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

function Tabs({
  currentTabIndexFromQuery,
  notification,
  showTestTab,
  setNotification,
  setUi,
  setUrl,
  tabs,
}: ITabs) {
  const [currentTabIndex, setCurrentTabIndex] = useState(currentTabIndexFromQuery);
  /** Once Run Test is opened, keep TestTab mounted so form/results state survives tab switches. */
  const [keepTestTabMounted, setKeepTestTabMounted] = useState(false);

  useEffect(() => {
    if (showTestTab) {
      setKeepTestTabMounted(true);
    }
  }, [showTestTab]);

  const onTabChange = (_: React.SyntheticEvent, index: number) => {
    const tab = tabs[index].key;
    setUi({ showTestTab: false });

    if (notification[tab]) {
      setNotification({ [tab]: false });
    }

    pushQuery({ tab });
    setUrl({ query: { tab } });
    setCurrentTabIndex(index);
  };

  useEffect(() => {
    setCurrentTabIndex(currentTabIndexFromQuery);
  }, [currentTabIndexFromQuery]);

  return (
    <Container maxWidth='xl'>
      <Box sx={{ mb: 2 }}>
        <MuiTabs
          onChange={onTabChange}
          scrollButtons='auto'
          value={showTestTab ? false : currentTabIndex}
          variant='scrollable'
        >
          {tabs.map(({ key: tabKey, title }, index) => (
            <MuiTab
              key={`tab-${index}`}
              label={<TabLabel hasNotification={notification[tabKey]} title={title} />}
            />
          ))}
        </MuiTabs>
      </Box>
      {keepTestTabMounted && (
        <Box sx={{ display: showTestTab ? 'block' : 'none' }}>
          <TestTab />
        </Box>
      )}
      {!showTestTab &&
        tabs.map(
          ({ component: Component = DataTable }, index) =>
            currentTabIndex === index && <Component key={`tabpabel-${index}`} />,
        )}
    </Container>
  );
}

const storeConnector = (
  state: IRootState,
  { tabs: tabsFromProps, extendedTabs: extendedTabsFromProps }: IStateProps,
) => {
  const {
    notification,
    ui: { showTestTab },
    swarm: { extendedTabs: extendedTabsFromState },
    url: { query: urlQuery },
  } = state;

  const tabs = tabsFromProps
    ? tabsFromProps
    : [...baseTabs, ...(extendedTabsFromProps || extendedTabsFromState || [])];

  const tabsToDisplay = tabs.filter(
    ({ shouldDisplayTab }) => !shouldDisplayTab || (shouldDisplayTab && shouldDisplayTab(state)),
  );

  const tabIndexFromQuery =
    urlQuery && urlQuery.tab ? tabsToDisplay.findIndex(({ key }) => key === urlQuery.tab) : 0;

  return {
    notification,
    showTestTab,
    tabs: tabsToDisplay,
    currentTabIndexFromQuery: tabIndexFromQuery > -1 ? tabIndexFromQuery : 0,
  };
};

const actionCreator = {
  setNotification: notificationActions.setNotification,
  setUi: uiActions.setUi,
  setUrl: urlActions.setUrl,
};

export default connect(storeConnector, actionCreator)(Tabs);
