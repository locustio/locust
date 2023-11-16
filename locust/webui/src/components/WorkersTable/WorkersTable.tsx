import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import useSortByField from 'hooks/useSortByField';
import { IRootState } from 'redux/store';
import { ISwarmWorker } from 'types/ui.types';
import { formatBytes } from 'utils/string';

const tableStructure = [
  { key: 'id', title: 'Worker' },
  { key: 'state', title: 'State' },
  { key: 'userCount', title: '# users' },
  { key: 'cpuUsage', title: 'CPU usage' },
  { key: 'memoryUsage', title: 'Memory usage', formatter: formatBytes },
];

function WorkersTable({ workers = [] }: { workers?: ISwarmWorker[] }) {
  const {
    onTableHeadClick,
    sortedStats: sortedWorkers,
    currentSortField,
  } = useSortByField<ISwarmWorker>(workers, { defaultSortKey: 'worker' as keyof ISwarmWorker });

  return (
    <Table<ISwarmWorker>
      currentSortField={currentSortField}
      onTableHeadClick={onTableHeadClick}
      rows={sortedWorkers}
      structure={tableStructure}
    />
  );
}

const storeConnector = ({ ui: { workers } }: IRootState) => ({ workers });

export default connect(storeConnector)(WorkersTable);
