import { useMemo } from 'react';

import Table from 'components/Table/Table';
import { IResponseTime } from 'types/ui.types';

interface IResponseTimeTable {
  hasMultipleHosts: boolean;
  responseTimes: IResponseTime[];
}

const tableStructure = [
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
];

export default function ResponseTimeTable({
  hasMultipleHosts,

  responseTimes,
}: IResponseTimeTable) {
  const percentileColumns = useMemo(
    () =>
      Object.keys(responseTimes[0])
        .filter(value => Boolean(Number(value)))
        .map(percentile => ({ key: percentile, title: `${Number(percentile) * 100}%ile (ms)` })),
    [responseTimes],
  );

  return (
    <Table<IResponseTime>
      groupOptions={hasMultipleHosts && ['host']}
      rows={responseTimes}
      structure={[...tableStructure, ...percentileColumns]}
    />
  );
}
