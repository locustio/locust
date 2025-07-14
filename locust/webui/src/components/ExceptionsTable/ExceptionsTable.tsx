import Table from 'components/Table/Table';
import { ISwarmException } from 'types/ui.types';

const tableStructure = [
  { key: 'count', title: '# occurrences' },
  { key: 'msg', title: 'Message' },
  { key: 'traceback', title: 'Traceback' },
];

export default function ExceptionsTable({ exceptions }: { exceptions: ISwarmException[] }) {
  return <Table<ISwarmException> rows={exceptions} structure={tableStructure} />;
}
