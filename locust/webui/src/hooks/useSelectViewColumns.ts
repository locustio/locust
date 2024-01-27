import { useState } from 'react';

import { ITableStructure } from 'types/table.types';

export default function useSelectViewColumns(defaultStructure: ITableStructure[]) {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(
    defaultStructure.map(column => column.key),
  );

  const filterStructure = (structure: ITableStructure[]) => {
    return structure.filter(s => selectedColumns.includes(s.key));
  };

  const addColumn = (column: string) => {
    setSelectedColumns([...selectedColumns, column]);
  };

  const removeColumn = (column: string) => {
    setSelectedColumns(selectedColumns.filter(c => c !== column));
  };

  return {
    selectedColumns,
    addColumn,
    removeColumn,
    filteredStructure: filterStructure(defaultStructure),
  };
}
