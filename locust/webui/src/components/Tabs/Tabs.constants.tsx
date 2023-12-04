import ExceptionsTable from 'components/ExceptionsTable/ExceptionsTable';
import FailuresTable from 'components/FailuresTable/FailuresTable';
import LogViewer from 'components/LogViewer/LogViewer';
import Reports from 'components/Reports/Reports';
import StatsTable from 'components/StatsTable/StatsTable';
import SwarmCharts from 'components/SwarmCharts/SwarmCharts';
import SwarmRatios from 'components/SwarmRatios/SwarmRatios';
import WorkersTable from 'components/WorkersTable/WorkersTable';
import { IRootState } from 'redux/store';

export const baseTabs = [
  {
    component: StatsTable,
    key: 'stats',
    title: 'Statistics',
  },
  {
    component: SwarmCharts,
    key: 'charts',
    title: 'Charts',
  },
  {
    component: FailuresTable,
    key: 'failures',
    title: 'Failures',
  },
  {
    component: ExceptionsTable,
    key: 'exceptions',
    title: 'Exceptions',
  },
  {
    component: SwarmRatios,
    key: 'ratios',
    title: 'Current Ratio',
  },
  {
    component: Reports,
    key: 'reports',
    title: 'Download Data',
  },
  {
    component: LogViewer,
    key: 'logViewer',
    title: 'Logs',
  },
];

export const conditionalTabs = [
  {
    component: WorkersTable,
    key: 'workers',
    title: 'Workers',
    shouldDisplayTab: (state: IRootState) => state.swarm.isDistributed,
  },
];
