import { Typography } from '@mui/material';
import { red, amber, blue } from '@mui/material/colors';

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

export default function LogDisplay({ log }: { log: string }) {
  return (
    <Typography color={getLogColor(log)} fontFamily={'monospace'} variant='body2'>
      {log}
    </Typography>
  );
}
