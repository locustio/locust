import { useEffect } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetTasksQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { uiActions } from 'redux/slice/ui.slice';

export default function useFetchTasks() {
  const { data: tasksData, refetch: refetchTasks } = useGetTasksQuery();
  const setUi = useAction(uiActions.setUi);

  const swarmState = useSelector(({ swarm }) => swarm.state);

  const shouldRunRefetchInterval =
    swarmState === SWARM_STATE.SPAWNING || swarmState == SWARM_STATE.RUNNING;

  useEffect(() => {
    if (tasksData) {
      setUi({ ratios: tasksData });
    }
  }, [tasksData]);

  useInterval(refetchTasks, 5000, {
    shouldRunInterval: shouldRunRefetchInterval,
    immediate: true,
  });
}
