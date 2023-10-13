import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import useSortByField from 'hooks/useSortByField';
import { IUiState } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';
import { ISwarmStat } from 'types/ui.types';

interface IStatsTable {
  groupBy?: string;
  canGroupBy?: boolean;
  hasMultipleHosts: boolean;
  stats: ISwarmStat[];
  updateUi?: (payload: Partial<IUiState>) => void;
}

const tableStructure = [
  { key: 'method', title: 'Type' },
  { key: 'name', title: 'Name' },
  { key: 'numRequests', title: '# Requests' },
  { key: 'numFailures', title: '# Fails' },
  { key: 'medianResponseTime', title: 'Median (ms)', round: 2 },
  { key: 'ninetiethResponseTime', title: '90%ile (ms)' },
  { key: 'ninetyNinthResponseTime', title: '99%ile (ms)' },
  { key: 'avgResponseTime', title: 'Average (ms)', round: 2 },
  { key: 'minResponseTime', title: 'Min (ms)' },
  { key: 'maxResponseTime', title: 'Max (ms)' },
  { key: 'avgContentLength', title: 'Average size (bytes)', round: 2 },
  { key: 'currentRps', title: 'Current RPS', round: 2 },
  { key: 'currentFailPerSec', title: 'Current Failures/s', round: 2 },
];

export function StatsTable({ canGroupBy = true, groupBy, hasMultipleHosts, stats }: IStatsTable) {
  const { onTableHeadClick, sortedStats, currentSortField } = useSortByField<ISwarmStat>(stats, {
    hasTotalRow: true,
  });

  return (
    <Table<ISwarmStat>
      currentSortField={currentSortField}
      groupBy={groupBy}
      groupOptions={canGroupBy && hasMultipleHosts && ['host']}
      label='stats'
      onTableHeadClick={onTableHeadClick}
      rows={sortedStats}
      structure={tableStructure}
    />
  );
}

const storeConnector = ({ swarm: { hasMultipleHosts }, ui: { stats } }: IRootState) => ({
  hasMultipleHosts: hasMultipleHosts && (stats.length === 1 || stats.some(({ host }) => host)),
  stats,
});

export default connect(storeConnector)(StatsTable);
