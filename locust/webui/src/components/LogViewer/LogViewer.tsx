import { Box, Typography } from '@mui/material';

import { useSelector } from 'redux/hooks';

export default function LogViewer() {
  const logs = useSelector(({ logViewer: { logs } }) => logs);

  return (
    <Box>
      <Typography component='h2' variant='h4'>
        Logs
      </Typography>

      <ul>
        {logs.map((log, index) => (
          <li key={`log-${index}`}>{log}</li>
        ))}
      </ul>
    </Box>
  );
}
