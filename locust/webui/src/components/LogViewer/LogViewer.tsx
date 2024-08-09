import { Box, Paper, Typography } from '@mui/material';

import LogDisplay from 'components/LogViewer/LogDisplay';
import WorkerLogs from 'components/LogViewer/WorkerLogs';
import { useSelector } from 'redux/hooks';
import { isEmpty } from 'utils/object';

export default function LogViewer() {
  const { master: masterLogs, workers: workerLogs } = useSelector(({ logViewer }) => logViewer);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4 }}>
      <Box>
        <Typography sx={{ mb: 2 }} variant='h5'>
          Master Logs
        </Typography>
        <Paper elevation={3} sx={{ p: 2, fontFamily: 'monospace' }}>
          {masterLogs.map((log, index) => (
            <LogDisplay key={`master-log-${index}`} log={log} />
          ))}
        </Paper>
      </Box>
      {!isEmpty(workerLogs) && (
        <Box>
          <Typography sx={{ mb: 2 }} variant='h5'>
            Worker Logs
          </Typography>
          {Object.entries(workerLogs).map(([workerId, logs], index) => (
            <WorkerLogs key={`worker-log-${index}`} logs={logs} workerId={workerId} />
          ))}
        </Box>
      )}
    </Box>
  );
}
