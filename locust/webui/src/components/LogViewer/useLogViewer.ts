import { useCallback, useEffect, useMemo } from 'react';

import { isImportantLog } from 'components/LogViewer/logUtils';
import { LOG_VIEWER_KEY } from 'constants/logs';
import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import useNotifications from 'hooks/useNotifications';
import { useGetLogsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { logViewerActions } from 'redux/slice/logViewer.slice';
import { flatten } from 'utils/array';

export default function useLogViewer() {
  const swarm = useSelector(({ swarm }) => swarm);
  const setLogs = useAction(logViewerActions.setLogs);
  const { data, refetch: refetchLogs } = useGetLogsQuery();

  const logs = data || { master: [], workers: {} };

  const workerLogs = useMemo(() => flatten<string>(Object.values(logs.workers)), [logs.workers]);
  const allLogs = [...logs.master, ...workerLogs];

  const shouldNotifyLogsUpdate = useCallback(
    () => allLogs.slice(localStorage['logViewer']).some(isImportantLog),
    [logs],
  );

  useInterval(refetchLogs, 5000, {
    shouldRunInterval: swarm.state === SWARM_STATE.SPAWNING || swarm.state == SWARM_STATE.RUNNING,
  });
  useNotifications(allLogs, {
    key: LOG_VIEWER_KEY,
    shouldNotify: shouldNotifyLogsUpdate,
  });

  useEffect(() => {
    setLogs(logs);
  }, [logs]);

  return logs;
}
