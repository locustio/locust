import { Button } from '@mui/material';

import { asyncRequest } from 'api/asyncRequest';

export default function ResetButton() {
  const onResetStatsClick = () => {
    asyncRequest('stats/reset');
  };

  return (
    <Button color='warning' onClick={onResetStatsClick} type='button' variant='contained'>
      Reset
    </Button>
  );
}
