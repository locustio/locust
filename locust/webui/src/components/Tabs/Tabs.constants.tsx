import ExceptionsTab from 'components/ExceptionsTab/ExceptionsTab';
import FailuresTable from 'components/FailuresTable/FailuresTableContainer';
import LogViewer from 'components/LogViewer/LogViewer';
import Reports from 'components/Reports/Reports';
import StatsTable from 'components/StatsTable/StatsTableContainer';
import SwarmCharts from 'components/SwarmCharts/SwarmChartsContainer';
import SwarmRatiosTab from 'components/SwarmRatiosTab/SwarmRatiosTab';
import WorkersTable from 'components/WorkersTable/WorkersTable';
import { LOG_VIEWER_KEY } from 'constants/logs';
import { IRootState } from 'redux/store';
import { ITab } from 'types/tab.types';

export const tabConfig = {
  stats: {
    component: StatsTable,
    key: 'stats',
    title: 'Statistics',
  },
  charts: {
    component: SwarmCharts,
    key: 'charts',
    title: 'Charts',
  },
  failures: {
    component: FailuresTable,
    key: 'failures',
    title: 'Failures',
  },
  exceptions: {
    component: ExceptionsTab,
    key: 'exceptions',
    title: 'Exceptions',
  },
  ratios: {
    component: SwarmRatiosTab,
    key: 'ratios',
    title: 'Current Ratio',
  },
  reports: {
    component: Reports,
    key: 'reports',
    title: 'Download Data',
  },
  logs: {
    component: LogViewer,
    key: LOG_VIEWER_KEY,
    title: 'Logs',
  },
  workers: {
    component: WorkersTable,
    key: 'workers',
    title: 'Workers',
    shouldDisplayTab: (state: IRootState) => state.swarm.isDistributed,
  },
};

export const baseTabs: ITab[] = [
  tabConfig.stats,
  tabConfig.charts,
  tabConfig.failures,
  tabConfig.exceptions,
  tabConfig.ratios,
  tabConfig.reports,
  tabConfig.logs,
  tabConfig.workers,
];
