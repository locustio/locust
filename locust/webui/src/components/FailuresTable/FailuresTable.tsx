import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import useSortByField from 'hooks/useSortByField';
import { IRootState } from 'redux/store';
import { ISwarmError } from 'types/ui.types';

const tableStructure = [
  { key: 'occurrences', title: '# Failures' },
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
  { key: 'error', title: 'Message', markdown: true },
];

export function FailuresTable({ errors }: { errors: ISwarmError[] }) {
  const {
    onTableHeadClick,
    sortedStats: sortedErrors,
    currentSortField,
  } = useSortByField<ISwarmError>(errors);

  return (
    <Table<ISwarmError>
      currentSortField={currentSortField}
      onTableHeadClick={onTableHeadClick}
      rows={sortedErrors}
      structure={tableStructure}
    />
  );
}

const storeConnector = ({ ui: { errors } }: IRootState) => ({ errors });

export default connect(storeConnector)(FailuresTable);
