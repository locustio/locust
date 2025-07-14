import ExceptionsTable from 'components/ExceptionsTable/ExceptionsTableContainer';
import useFetchExceptions from 'hooks/useFetchExceptions';

export default function ExceptionsTab() {
  useFetchExceptions();

  return <ExceptionsTable />;
}
