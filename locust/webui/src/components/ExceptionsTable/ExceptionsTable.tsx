import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import { IRootState } from 'redux/store';
import { ISwarmException } from 'types/ui.types';

const tableStructure = [
  { key: 'count', title: '# occurrences' },
  { key: 'traceback', title: 'Traceback' },
];

export function ExceptionsTable({ exceptions }: { exceptions: ISwarmException[] }) {
  return <Table<ISwarmException> rows={exceptions} structure={tableStructure} />;
}

const storeConnector = ({ ui: { exceptions } }: IRootState) => ({ exceptions });

export default connect(storeConnector)(ExceptionsTable);
