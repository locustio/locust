import { useEffect, useState } from 'react';
import { Button } from '@mui/material';

import { useStopSwarmMutation } from 'redux/api/swarm';

export default function StopButton() {
  const [isLoading, setIsLoading] = useState(false);
  const [stopSwarm] = useStopSwarmMutation()
  

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const onStopButtonClick = () => {
    stopSwarm()
    setIsLoading(true);
  };

  return (
    <Button
      color='error'
      disabled={isLoading}
      onClick={onStopButtonClick}
      type='button'
      variant='contained'
    >
      {isLoading ? 'Loading' : 'Stop'}
    </Button>
  );
}
