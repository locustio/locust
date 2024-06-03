import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Paper,
  Typography,
} from '@mui/material';
import { red, amber, blue } from '@mui/material/colors';

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
    <Typography color={getLogColor(log)} variant='body2'>
      {log}
    </Typography>
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
            <Accordion key={`worker-log-${index}`}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>{workerId}</AccordionSummary>
              <AccordionDetails>
                <Paper elevation={3} sx={{ p: 2, fontFamily: 'monospace' }}>
                  {logs.map((log, index) => (
                    <LogDisplay key={`worker-${workerId}-log-${index}`} log={log} />
                  ))}
                </Paper>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
}
