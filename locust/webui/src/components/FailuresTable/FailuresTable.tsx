import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import { IRootState } from 'redux/store';
import { ISwarmError } from 'types/ui.types';

const tableStructure = [
  { key: 'occurrences', title: '# Failures' },
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
  { key: 'error', title: 'Message', markdown: true },
];

export function FailuresTable({ errors }: { errors: ISwarmError[] }) {
  return <Table<ISwarmError> rows={errors} structure={tableStructure} />;
}

const storeConnector = ({ ui: { errors } }: IRootState) => ({ errors });

export default connect(storeConnector)(FailuresTable);
