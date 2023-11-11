import { useCallback, useEffect, useRef, useState } from 'react';

function sortByField<IStat>(field: keyof IStat, reverse: boolean) {
  const reverseModifier = reverse ? -1 : 1;

  return function (a: IStat, b: IStat) {
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

export default function useSortByField<IStat>(
  stats: IStat[],
  {
    hasTotalRow = false,
    defaultSortKey = 'name' as keyof IStat,
  }: { hasTotalRow?: boolean; defaultSortKey?: keyof IStat } = {
    hasTotalRow: false,
    defaultSortKey: 'name' as keyof IStat,
  },
) {
  const [sortedStats, setSortedStats] = useState(stats);
  const [shouldReverse, setShouldReverse] = useState(false);
  const currentSortField = useRef<keyof IStat>();

  const sortStats = (sortField: keyof IStat) => {
    const statsToSort = hasTotalRow ? stats.slice(0, -1) : [...stats];
    const sortedStats = statsToSort.sort(
      // reverse will only happen when clicking twice on the same field
      sortByField<IStat>(sortField, sortField === currentSortField.current && !shouldReverse),
    );

    setSortedStats(hasTotalRow ? [...sortedStats, ...stats.slice(-1)] : sortedStats);
  };

  const onTableHeadClick = useCallback(
    (event: React.MouseEvent<HTMLElement>) => {
      if (!currentSortField.current) {
        currentSortField.current = defaultSortKey;
      }

      const sortField = (event.target as HTMLElement).getAttribute('data-sortkey') as keyof IStat;

      if (sortField === currentSortField.current) {
        if (shouldReverse) {
          // reset to intial state on 3rd click
          setShouldReverse(false);
          currentSortField.current = undefined;
          setSortedStats(stats);
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
    [currentSortField, stats, shouldReverse],
  );

  useEffect(() => {
    if (stats.length) {
      sortStats(currentSortField.current || defaultSortKey);
    }
  }, [stats]);

  return {
    onTableHeadClick,
    sortedStats,
    currentSortField: currentSortField.current,
  };
}
