import { useEffect } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetWorkerCountQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';

const WORKER_COUNT_REFETCH_INTERVAL = 2000;

export default function useFetchWorkerCount() {
  const { data: workerCountData, refetch: refetchWorkerCount } = useGetWorkerCountQuery();
  const setSwarm = useAction(swarmActions.setSwarm);
  const swarm = useSelector(({ swarm }) => swarm);

  useEffect(() => {
    if (!workerCountData) {
      return;
    }

    setSwarm({ workerCount: workerCountData.workerCount });
  }, [workerCountData]);

  useInterval(refetchWorkerCount, WORKER_COUNT_REFETCH_INTERVAL, {
    shouldRunInterval: swarm.isDistributed && swarm.state === SWARM_STATE.READY,
  });
}
