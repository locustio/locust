import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import { IRootState } from 'redux/store';
import { ISwarmWorker } from 'types/ui.types';

const tableStructure = [
  { key: 'id', title: 'Worker' },
  { key: 'state', title: 'State' },
  { key: 'userCount', title: '# users' },
  { key: 'cpuUsage', title: 'CPU usage' },
  { key: 'memoryUsage', title: 'Memory usage' },
];

function WorkersTable({ workers = [] }: { workers?: ISwarmWorker[] }) {
  return <Table<ISwarmWorker> rows={workers} structure={tableStructure} />;
}

const storeConnector = ({ ui: { workers } }: IRootState) => ({ workers });

export default connect(storeConnector)(WorkersTable);
