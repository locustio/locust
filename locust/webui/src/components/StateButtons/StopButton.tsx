import { useEffect, useState } from 'react';
import { Button } from '@mui/material';

export default function StopButton() {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const onStopButtonClick = () => {
    fetch('stop');
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
