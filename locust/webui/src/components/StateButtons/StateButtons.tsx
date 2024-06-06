import { Box } from '@mui/material';

import EditButton from 'components/StateButtons/EditButton';
import NewTestButton from 'components/StateButtons/NewTestButton';
import ResetButton from 'components/StateButtons/ResetButton';
import StopButton from 'components/StateButtons/StopButton';
import { SWARM_STATE } from 'constants/swarm';
import { useSelector } from 'redux/hooks';

export default function StateButtons() {
  const swarmState = useSelector(({ swarm }) => swarm.state);

  if (swarmState === SWARM_STATE.READY) {
    return null;
  }

  return (
    <Box sx={{ display: 'flex', columnGap: 2 }}>
      {swarmState === SWARM_STATE.STOPPED ? (
        <NewTestButton />
      ) : (
        <>
          <EditButton />
          <StopButton />
        </>
      )}
      <ResetButton />
    </Box>
  );
}
