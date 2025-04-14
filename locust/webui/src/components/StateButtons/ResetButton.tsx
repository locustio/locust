import { Button } from '@mui/material';

export default function ResetButton() {
  const onResetStatsClick = () => {
    fetch(
      (window.baseUrl ? `${window.baseUrl}/` : '') + 'stats/reset',
      window.baseUrl ? { credentials: 'include' } : undefined,
    );
  };

  return (
    <Button color='warning' onClick={onResetStatsClick} type='button' variant='contained'>
      Reset
    </Button>
  );
}
