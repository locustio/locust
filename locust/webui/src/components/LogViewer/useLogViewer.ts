import { useEffect } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import useNotifications from 'hooks/useNotifications';
import { useGetLogsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { logViewerActions } from 'redux/slice/logViewer.slice';

export default function useLogViewer() {
  const swarm = useSelector(({ swarm }) => swarm);
  const setLogs = useAction(logViewerActions.setLogs);
  const { data, refetch: refetchLogs } = useGetLogsQuery();

  const logs = data ? data.logs : [];

  useInterval(refetchLogs, 5000, {
    shouldRunInterval: swarm.state === SWARM_STATE.SPAWNING || swarm.state == SWARM_STATE.RUNNING,
  });
  useNotifications(logs, { key: 'logViewer' });

  useEffect(() => {
    setLogs({ logs });
  }, [logs]);

  return logs;
}
