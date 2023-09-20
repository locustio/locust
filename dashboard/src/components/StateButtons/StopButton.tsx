import { useEffect, useState } from 'react';
import { Button } from '@mui/material';

import { asyncRequest } from 'api/asyncRequest';

export default function StopButton() {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const onStopButtonClick = () => {
    asyncRequest('stop');
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
