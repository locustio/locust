import { useCallback, useMemo, useState } from 'react';

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
  const [sortField, setSortField] = useState<keyof Row | undefined>(undefined);
  const [shouldReverse, setShouldReverse] = useState(false);

  const onTableHeadClick = useCallback(
    (event: React.MouseEvent<HTMLElement>) => {
      const selectedSortField = (event.target as HTMLElement).getAttribute(
        'data-sortkey',
      ) as keyof Row;

      if (selectedSortField === sortField) {
        if (shouldReverse) {
          // reset to initial state on 3rd click
          setShouldReverse(false);
          setSortField(undefined);
          return;
        } else {
          setShouldReverse(true);
        }
      } else if (shouldReverse) {
        // reset reverse when sorting by new field
        setShouldReverse(false);
      }

      setSortField(selectedSortField);
    },
    [rows, shouldReverse, sortField],
  );

  const sortedRows = useMemo(() => {
    const rowsToSort = hasTotalRow ? rows.slice(0, -1) : [...rows];
    const sortedRows = rowsToSort.sort(
      // reverse will only happen when clicking twice on the same field
      sortByField<Row>(sortField || defaultSortKey, shouldReverse),
    );

    return hasTotalRow ? [...sortedRows, ...rows.slice(-1)] : sortedRows;
  }, [rows, sortField, shouldReverse]);

  return {
    onTableHeadClick,
    sortedRows,
    currentSortField: sortField,
  };
}
