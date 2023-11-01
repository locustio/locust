import { Box, Typography } from '@mui/material';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetLogsQuery } from 'redux/api/swarm';
import { useSelector } from 'redux/hooks';

export default function LogViewer() {
  const swarm = useSelector(({ swarm }) => swarm);
  const { data, refetch: refetchLogs } = useGetLogsQuery();

  useInterval(refetchLogs, 5000, { shouldRunInterval: swarm.state !== SWARM_STATE.STOPPED });

  return (
    <Box>
      <Typography component='h2' variant='h4'>
        Logs
      </Typography>

      <ul>{data && data.logs.map((log, index) => <li key={`log-${index}`}>{log}</li>)}</ul>
    </Box>
  );
}
