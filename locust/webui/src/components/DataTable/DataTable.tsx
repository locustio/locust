import { connect } from 'react-redux';

import Table from 'components/Table/Table';
import { IRootState } from 'redux/store';
import { ITableStructure } from 'types/table.types';
import { IExtendedStatData } from 'types/ui.types';
import { snakeToCamelCase } from 'utils/string';

interface IDataTable {
  rows: IExtendedStatData[] | never[];
  tableStructure: ITableStructure[] | null;
}

function DataTable({ rows, tableStructure }: IDataTable) {
  if (!tableStructure) {
    return null;
  }

  return <Table<IExtendedStatData> rows={rows} structure={tableStructure} />;
}

const storeConnector = ({
  swarm: { extendedTables },
  ui: { extendedStats },
  url: { query },
}: IRootState) => {
  const tableStructure =
    query && query.tab && extendedTables && extendedTables.find(({ key }) => key === query.tab);

  const tableExtendedStats =
    query && query.tab && extendedStats && extendedStats.find(({ key }) => key === query.tab);

  return {
    tableStructure: tableStructure
      ? tableStructure.structure.map(({ key, ...structure }) => ({
          key: snakeToCamelCase(key),
          ...structure,
        }))
      : null,
    rows: tableExtendedStats ? tableExtendedStats.data : [],
  };
};

export default connect(storeConnector)(DataTable);
