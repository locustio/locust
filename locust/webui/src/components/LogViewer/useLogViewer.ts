import { useCallback, useEffect, useMemo } from 'react';

import { isImportantLog } from 'components/LogViewer/LogViewer.utils';
import { LOG_VIEWER_KEY } from 'constants/logs';
import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import useNotifications from 'hooks/useNotifications';
import { useGetLogsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { logViewerActions } from 'redux/slice/logViewer.slice';
import { flatten } from 'utils/array';

const defaultLogs = { master: [], workers: {} };

export default function useLogViewer() {
  const swarm = useSelector(({ swarm }) => swarm);
  const setLogs = useAction(logViewerActions.setLogs);
  const { data, refetch: refetchLogs } = useGetLogsQuery();

  const logs = data || defaultLogs;

  const workerLogs = useMemo(() => flatten<string>(Object.values(logs.workers)), [logs.workers]);
  const allLogs = useMemo(() => [...logs.master].concat(workerLogs), [logs.master, logs.workers]);

  const shouldNotifyLogsUpdate = useCallback(
    (key: string) => allLogs.slice(localStorage[key]).some(isImportantLog),
    [allLogs],
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
