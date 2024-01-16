import { useState } from 'react';

import { ITableStructure } from 'types/table.types';

export default function useSelectViewColumns(defaultColumns: string[]) {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(defaultColumns);

  const addColumn = (column: string) => {
    setSelectedColumns([...selectedColumns, column]);
  };

  const removeColumn = (column: string) => {
    setSelectedColumns(selectedColumns.filter(c => c !== column));
  };

  const filterStructure = (structure: ITableStructure[]) => {
    return structure.filter(s => selectedColumns.includes(s.key));
  };

  return {
    selectedColumns,
    addColumn,
    removeColumn,
    filterStructure,
  };
}
