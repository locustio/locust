import SwarmRatios from 'components/SwarmRatios/SwarmRatios';
import useFetchTasks from 'hooks/useFetchTasks';

export default function SwarmRatiosTab() {
  useFetchTasks();

  return <SwarmRatios />;
}
