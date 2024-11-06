import ExceptionsTable from 'components/ExceptionsTable/ExceptionsTable';
import useFetchExceptions from 'hooks/useFetchExceptions';

export default function ExceptionsTab() {
  useFetchExceptions();

  return <ExceptionsTable />;
}
