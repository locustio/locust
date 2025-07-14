import Table from 'components/Table/Table';
import { ISwarmError } from 'types/ui.types';

const tableStructure = [
  { key: 'occurrences', title: '# Failures' },
  { key: 'method', title: 'Method' },
  { key: 'name', title: 'Name' },
  { key: 'error', title: 'Message' },
];

export default function FailuresTable({ errors }: { errors: ISwarmError[] }) {
  return <Table<ISwarmError> rows={errors} structure={tableStructure} />;
}
