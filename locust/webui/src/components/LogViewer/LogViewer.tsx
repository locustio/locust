import { useEffect, useState } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Paper,
  Typography,
} from '@mui/material';
import { red, amber, blue } from '@mui/material/colors';

import { isImportantLog } from 'components/LogViewer/logUtils';
import { useSelector } from 'redux/hooks';
import { objectLength } from 'utils/object';

const getLogColor = (log: string) => {
  if (log.includes('CRITICAL')) {
    return red[900];
  }
  if (log.includes('ERROR')) {
    return red[700];
  }
  if (log.includes('WARNING')) {
    return amber[900];
  }
  if (log.includes('DEBUG')) {
    return blue[700];
  }
  return 'text.primary';
};

function LogDisplay({ log }: { log: string }) {
  return (
    <Typography color={getLogColor(log)} fontFamily={'monospace'} variant='body2'>
      {log}
    </Typography>
  );
}

function WorkerLogs({ workerId, logs }: { workerId: string; logs: string[] }) {
  const [hasImportantLog, setHasImportantLog] = useState(false);

  useEffect(() => {
    if (logs.some(isImportantLog)) {
      setHasImportantLog(true);
    }
  }, [logs]);

  return (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />} onClick={() => setHasImportantLog(false)}>
        {hasImportantLog && <PriorityHighIcon color='secondary' />}
        {workerId}
      </AccordionSummary>
      <AccordionDetails>
        <Paper elevation={3} sx={{ p: 2 }}>
          {logs.map((log, index) => (
            <LogDisplay key={`worker-${workerId}-log-${index}`} log={log} />
          ))}
        </Paper>
      </AccordionDetails>
    </Accordion>
  );
}

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
      {!!objectLength(workerLogs) && (
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
