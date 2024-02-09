import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import ViewColumnSelector from 'components/ViewColumnSelector/ViewColumnSelector';
import { swarmTemplateArgs } from 'constants/swarm';
import useSelectViewColumns from 'hooks/useSelectViewColumns';
import { IRootState } from 'redux/store';
import { ISwarmStat } from 'types/ui.types';

const percentilesToStatisticsRows = swarmTemplateArgs.percentilesToStatistics
  ? swarmTemplateArgs.percentilesToStatistics.map(percentile => ({
      title: `${percentile * 100}%ile (ms)`,
      key: `responseTimePercentile${percentile}` as keyof ISwarmStat,
    }))
  : [];

const tableStructure = [
  { key: 'method', title: 'Type' },
  { key: 'name', title: 'Name' },
  { key: 'numRequests', title: '# Requests' },
  { key: 'numFailures', title: '# Fails' },
  { key: 'medianResponseTime', title: 'Median (ms)', round: 2 },
  ...percentilesToStatisticsRows,
  { key: 'avgResponseTime', title: 'Average (ms)', round: 2 },
  { key: 'minResponseTime', title: 'Min (ms)' },
  { key: 'maxResponseTime', title: 'Max (ms)' },
  { key: 'avgContentLength', title: 'Average size (bytes)', round: 2 },
  { key: 'currentRps', title: 'Current RPS', round: 2 },
  { key: 'currentFailPerSec', title: 'Current Failures/s', round: 2 },
];

export function StatsTable({ stats }: { stats: ISwarmStat[] }) {
  const { selectedColumns, addColumn, removeColumn, filteredStructure } =
    useSelectViewColumns(tableStructure);

  return (
    <>
      <ViewColumnSelector
        addColumn={addColumn}
        removeColumn={removeColumn}
        selectedColumns={selectedColumns}
        structure={tableStructure}
      />
      <Table<ISwarmStat> hasTotalRow rows={stats} structure={filteredStructure} />
    </>
  );
}

const storeConnector = ({ ui: { stats } }: IRootState) => ({ stats });

export default connect(storeConnector)(StatsTable);
