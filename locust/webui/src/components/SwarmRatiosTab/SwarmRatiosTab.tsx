import SwarmRatios from 'components/SwarmRatios/SwarmRatiosContainer';
import useFetchTasks from 'hooks/useFetchTasks';

export default function SwarmRatiosTab() {
  useFetchTasks();

  return <SwarmRatios />;
}
