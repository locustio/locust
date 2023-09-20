import { useState } from 'react';
import { Box, Tabs as MuiTabs, Tab as MuiTab, Container } from '@mui/material';
import { connect } from 'react-redux';

import { ITab, baseTabs, conditionalTabs } from 'components/Tabs/Tabs.constants';
import { IUrlState, urlActions } from 'redux/slice/url.slice';
import { IRootState } from 'redux/store';
import { pushQuery } from 'utils/url';

interface ITabs {
  currentTabIndexFromQuery: number;
  setUrl: (payload: IUrlState) => void;
  tabs: ITab[];
}

function Tabs({ currentTabIndexFromQuery, setUrl, tabs }: ITabs) {
  const [currentTabIndex, setCurrentTabIndex] = useState(currentTabIndexFromQuery);

  const onTabChange = (_: React.SyntheticEvent, index: number) => {
    const tab = tabs[index].key;
    pushQuery({ tab });
    setUrl({ query: { tab } });
    setCurrentTabIndex(index);
  };

  return (
    <Container maxWidth='xl'>
      <Box sx={{ mb: 2 }}>
        <MuiTabs onChange={onTabChange} value={currentTabIndex}>
          {tabs.map(({ title }, index) => (
            <MuiTab key={`tab-${index}`} label={title} />
          ))}
        </MuiTabs>
      </Box>
      {tabs.map(
        ({ component: Component }, index) =>
          currentTabIndex === index && <Component key={`tabpabel-${index}`} />,
      )}
    </Container>
  );
}

const storeConnector = (state: IRootState) => {
  const {
    url: { query: urlQuery },
  } = state;

  const conditionalTabsToDisplay = conditionalTabs.filter(({ shouldDisplayTab }) =>
    shouldDisplayTab(state),
  );

  const tabs = [...baseTabs, ...conditionalTabsToDisplay];

  return {
    tabs,
    currentTabIndexFromQuery:
      urlQuery && urlQuery.tab ? tabs.findIndex(({ key }) => key === urlQuery.tab) : 0,
  };
};

const actionCreator = {
  setUrl: urlActions.setUrl,
};

export default connect(storeConnector, actionCreator)(Tabs);
