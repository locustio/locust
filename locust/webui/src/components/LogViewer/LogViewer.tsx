import { Box, Paper, Typography } from '@mui/material';
import { red, amber, blue } from '@mui/material/colors';

import { useSelector } from 'redux/hooks';

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

export default function LogViewer() {
  const logs = useSelector(({ logViewer: { logs } }) => logs);

  return (
    <Box>
      <Typography sx={{ mb: 2 }} variant='h5'>
        Logs
      </Typography>
      <Paper elevation={3} sx={{ p: 2, fontFamily: 'monospace' }}>
        {logs.map((log, index) => (
          <Typography color={getLogColor(log)} key={`log-${index}`} variant='body2'>
            {log}
          </Typography>
        ))}
      </Paper>
    </Box>
  );
}
