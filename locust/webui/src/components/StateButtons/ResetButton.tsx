import { Button } from '@mui/material';

import { useDispatch } from 'redux/hooks';
import { useResetStatsMutation } from 'redux/api/swarm';
import { uiActions } from 'redux/slice/ui.slice';

export default function ResetButton() {
  const [resetStats] = useResetStatsMutation();
  const dispatch = useDispatch();

  const onResetStatsClick = () => {
    resetStats();
    dispatch(uiActions.setUi({ testTabResetNonce: Date.now() }));
  };

  return (
    <Button color='warning' onClick={onResetStatsClick} type='button' variant='contained'>
      Reset
    </Button>
  );
}
