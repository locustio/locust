import { useEffect } from 'react';
import { SWARM_STATE, useInterval } from 'lib';

import { useGetExceptionsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { uiActions } from 'redux/slice/ui.slice';

export default function useFetchExceptions() {
  const { data: exceptionsData, refetch: refetchExceptions } = useGetExceptionsQuery();
  const setUi = useAction(uiActions.setUi);

  const swarmState = useSelector(({ swarm }) => swarm.state);

  const shouldRunRefetchInterval =
    swarmState === SWARM_STATE.SPAWNING || swarmState == SWARM_STATE.RUNNING;

  useEffect(() => {
    if (exceptionsData) {
      setUi({ exceptions: exceptionsData.exceptions });
    }
  }, [exceptionsData]);

  useInterval(refetchExceptions, 5000, {
    shouldRunInterval: shouldRunRefetchInterval,
  });
}
