import { useCallback, useEffect, useRef, useState } from 'react';

export interface ISortByFieldOptions<Row> {
  hasTotalRow?: boolean;
  defaultSortKey?: keyof Row;
}

function sortByField<Row>(field: keyof Row, reverse: boolean) {
  const reverseModifier = reverse ? -1 : 1;

  return function (a: Row, b: Row) {
    const valueA = a[field];
    const valueB = b[field];

    if (valueA < valueB) {
      return reverseModifier * -1;
    }

    if (valueA > valueB) {
      return reverseModifier * 1;
    }

    return 0;
  };
}

export default function useSortByField<Row>(
  rows: Row[],
  { hasTotalRow = false, defaultSortKey = 'name' as keyof Row }: ISortByFieldOptions<Row> = {
    hasTotalRow: false,
    defaultSortKey: 'name' as keyof Row,
  },
) {
  const [sortedRows, setSortedRows] = useState(rows);
  const [shouldReverse, setShouldReverse] = useState(false);
  const currentSortField = useRef<keyof Row>();

  const sortStats = (sortField: keyof Row) => {
    const rowsToSort = hasTotalRow ? rows.slice(0, -1) : [...rows];
    const sortedRows = rowsToSort.sort(
      // reverse will only happen when clicking twice on the same field
      sortByField<Row>(sortField, sortField === currentSortField.current && !shouldReverse),
    );

    setSortedRows(hasTotalRow ? [...sortedRows, ...rows.slice(-1)] : sortedRows);
  };

  const onTableHeadClick = useCallback(
    (event: React.MouseEvent<HTMLElement>) => {
      if (!currentSortField.current) {
        currentSortField.current = defaultSortKey;
      }

      const sortField = (event.target as HTMLElement).getAttribute('data-sortkey') as keyof Row;

      if (sortField === currentSortField.current) {
        if (shouldReverse) {
          // reset to initial state on 3rd click
          setShouldReverse(false);
          currentSortField.current = undefined;
          sortStats(defaultSortKey);
          return;
        } else {
          setShouldReverse(true);
        }
      } else if (shouldReverse) {
        // reset reverse when sorting by new field
        setShouldReverse(false);
      }

      sortStats(sortField);
      currentSortField.current = sortField;
    },
    [currentSortField, rows, shouldReverse],
  );

  useEffect(() => {
    if (rows.length) {
      sortStats(currentSortField.current || defaultSortKey);
    }
  }, [rows]);

  return {
    onTableHeadClick,
    sortedRows,
    currentSortField: currentSortField.current,
  };
}
