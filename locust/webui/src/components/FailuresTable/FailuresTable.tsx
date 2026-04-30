import Table from 'components/Table/Table';
import { ISwarmError } from 'types/ui.types';

type IFailuresTableRow = Omit<ISwarmError, 'firstSeen' | 'lastSeen'> & {
  firstSeen: string;
  lastSeen: string;
};

const formatTimestamp = (unixSeconds: number | null) =>
  unixSeconds ? new Date(unixSeconds * 1000).toLocaleString() : '';

const tableStructure = [
  { key: 'occurrences', title: '# Failures' },
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
  { key: 'error', title: 'Message' },
  { key: 'firstSeen', title: 'First Seen' },
  { key: 'lastSeen', title: 'Last Seen' },
];

export default function FailuresTable({ errors }: { errors: ISwarmError[] }) {
  const rows: IFailuresTableRow[] = errors.map(error => ({
    ...error,
    firstSeen: formatTimestamp(error.firstSeen),
    lastSeen: formatTimestamp(error.lastSeen),
  }));
  return <Table<IFailuresTableRow> rows={rows} structure={tableStructure} />;
}
