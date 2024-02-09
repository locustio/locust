import { useMemo } from 'react';

import Table from 'components/Table/Table';
import { IResponseTime } from 'types/ui.types';

const tableStructure = [
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
];

interface IResponseTimeTable {
  responseTimes: IResponseTime[];
}

export default function ResponseTimeTable({ responseTimes }: IResponseTimeTable) {
  const percentileColumns = useMemo(
    () =>
      Object.keys(responseTimes[0])
        .filter(value => Boolean(Number(value)))
        .map(percentile => ({ key: percentile, title: `${Number(percentile) * 100}%ile (ms)` })),
    [responseTimes],
  );

  return (
    <Table hasTotalRow rows={responseTimes} structure={[...tableStructure, ...percentileColumns]} />
  );
}
