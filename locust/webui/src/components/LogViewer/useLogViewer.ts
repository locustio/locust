import { useCallback, useEffect } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import useNotifications from 'hooks/useNotifications';
import { useGetLogsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { logViewerActions } from 'redux/slice/logViewer.slice';

const isImportantLog = (log: string) =>
  log.includes('WARNING') || log.includes('ERROR') || log.includes('CRITICAL');

export default function useLogViewer() {
  const swarm = useSelector(({ swarm }) => swarm);
  const setLogs = useAction(logViewerActions.setLogs);
  const { data, refetch: refetchLogs } = useGetLogsQuery();

  const logs = data ? data.logs : [];

  const shouldNotifyLogsUpdate = useCallback(
    () => logs.slice(localStorage['logViewer']).some(isImportantLog),
    [logs],
  );

  useInterval(refetchLogs, 5000, {
    shouldRunInterval: swarm.state === SWARM_STATE.SPAWNING || swarm.state == SWARM_STATE.RUNNING,
  });
  useNotifications(logs, { key: 'logViewer', shouldNotify: shouldNotifyLogsUpdate });

  useEffect(() => {
    setLogs({ logs });
  }, [logs]);

  return logs;
}
