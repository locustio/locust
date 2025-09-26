import Table from 'components/Table/Table';
import ViewColumnSelector from 'components/ViewColumnSelector/ViewColumnSelector';
import { swarmTemplateArgs } from 'constants/swarm';
import useSelectViewColumns from 'hooks/useSelectViewColumns';
import { ITableStructure } from 'types/table.types';
import { ISwarmStat } from 'types/ui.types';

const percentilesToStatisticsRows = swarmTemplateArgs.percentilesToStatistics
  ? swarmTemplateArgs.percentilesToStatistics.map(percentile => ({
      title: `${percentile * 100}%ile (ms)`,
      key: `responseTimePercentile${percentile}` as keyof ISwarmStat,
    }))
  : [];

export const baseTableStructure = [
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

interface IStatsTable {
  stats: ISwarmStat[];
  tableStructure?: ITableStructure[];
}

export default function StatsTable({ stats, tableStructure = baseTableStructure }: IStatsTable) {
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
