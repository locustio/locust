import { useState, useEffect } from 'react';

import { ITableStructure } from 'types/table.types';
import { ISwarmStat } from 'types/ui.types';

export default function useSelectViewColumns(defaultStructure: ITableStructure[], stats: ISwarmStat[]) {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(
    defaultStructure.filter(column => !column.hidden).map(column => column.key),
  );

  const filterColumnsWithData = (structure: ITableStructure[], stats: ISwarmStat[]) => {
    return structure.filter(column => stats.some(stat => stat[column.key] !== undefined && stat[column.key] !== null));
  };

  useEffect(() => {
    const columnsWithData = filterColumnsWithData(defaultStructure, stats).map(column => column.key);
    setSelectedColumns(columnsWithData);
  }, [stats]);

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
