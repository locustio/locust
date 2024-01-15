import { useState } from 'react';

export default function useSelectViewColumns(defaultColumns: string[]) {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(defaultColumns);

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
  };
}
