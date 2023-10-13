import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import useSortByField from 'hooks/useSortByField';
import { IUiState } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';
import { ISwarmError } from 'types/ui.types';

interface IFailuresTable {
  groupBy?: string;
  canGroupBy?: boolean;
  errors: ISwarmError[];
  hasMultipleHosts: boolean;
  updateUi?: (payload: Partial<IUiState>) => void;
}

const tableStructure = [
  { key: 'occurrences', title: '# Failures' },
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
  { key: 'error', title: 'Message', markdown: true },
];

export function FailuresTable({
  canGroupBy = true,
  groupBy,
  errors,
  hasMultipleHosts,
}: IFailuresTable) {
  const {
    onTableHeadClick,
    sortedStats: sortedErrors,
    currentSortField,
  } = useSortByField<ISwarmError>(errors);

  return (
    <Table<ISwarmError>
      currentSortField={currentSortField}
      groupBy={groupBy}
      groupOptions={canGroupBy && hasMultipleHosts && ['host']}
      label='failures'
      onTableHeadClick={onTableHeadClick}
      rows={sortedErrors}
      structure={tableStructure}
    />
  );
}

const storeConnector = ({ swarm: { hasMultipleHosts }, ui: { errors } }: IRootState) => ({
  errors,
  hasMultipleHosts: hasMultipleHosts && (!errors.length || errors.some(({ host }) => host)),
});

export default connect(storeConnector)(FailuresTable);
