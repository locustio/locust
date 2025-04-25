import { Button } from '@mui/material';

import { useResetStatsMutation } from 'redux/api/swarm';

export default function ResetButton() {
  const [resetStats] = useResetStatsMutation()

  const onResetStatsClick = () => {
    resetStats()
  };

  return (
    <Button color='warning' onClick={onResetStatsClick} type='button' variant='contained'>
      Reset
    </Button>
  );
}
