import { useCallback, useEffect, useState } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import { Accordion, AccordionDetails, AccordionSummary, Paper } from '@mui/material';

import LogDisplay from 'components/LogViewer/LogDisplay';
import { isImportantLog } from 'components/LogViewer/LogViewer.utils';

export default function WorkerLogs({ workerId, logs }: { workerId: string; logs: string[] }) {
  const [hasImportantLog, setHasImportantLog] = useState(false);

  useEffect(() => {
    if (logs.slice(localStorage[workerId]).some(isImportantLog)) {
      setHasImportantLog(true);
    }
  }, [logs]);

  const onExpandLogs = useCallback(() => {
    setHasImportantLog(false);
    localStorage[workerId] = logs.length;
  }, []);

  return (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />} onClick={onExpandLogs}>
        {hasImportantLog && (
          <PriorityHighIcon color='secondary' data-testid='worker-notification' />
        )}
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
