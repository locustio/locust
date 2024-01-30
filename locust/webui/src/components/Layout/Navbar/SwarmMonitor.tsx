import { Box, Divider, Typography } from '@mui/material';
import { connect } from 'react-redux';

import { SWARM_STATE } from 'constants/swarm';
import { ISwarmState } from 'redux/slice/swarm.slice';
import { IUiState } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';

interface ISwarmMonitor
  extends Pick<ISwarmState, 'isDistributed' | 'host' | 'state' | 'workerCount'>,
    Pick<IUiState, 'totalRps' | 'failRatio' | 'userCount'> {}

function SwarmMonitor({
  isDistributed,
  state,
  host,
  totalRps,
  failRatio,
  userCount,
  workerCount,
}: ISwarmMonitor) {
  return (
    <Box sx={{ display: 'flex', columnGap: 2 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
        <Typography variant='button'>Host</Typography>
        <Typography>{host}</Typography>
      </Box>
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
        <Typography variant='button'>Status</Typography>
        <Typography variant='button'>{state}</Typography>
      </Box>
      {(state === SWARM_STATE.RUNNING || state === SWARM_STATE.SPAWNING) && (
        <>
          <Divider flexItem orientation='vertical' />
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant='button'>Users</Typography>
            <Typography variant='button'>{userCount}</Typography>
          </Box>
        </>
      )}
      {isDistributed && (
        <>
          <Divider flexItem orientation='vertical' />
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant='button'>Workers</Typography>
            <Typography variant='button'>{workerCount}</Typography>
          </Box>
        </>
      )}
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant='button'>RPS</Typography>
        <Typography variant='button'>{totalRps}</Typography>
      </Box>
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant='button'>Failures</Typography>
        <Typography variant='button'>{`${failRatio}%`}</Typography>
      </Box>
    </Box>
  );
}

const storeConnector = ({
  swarm: { isDistributed, state, host, workerCount },
  ui: { totalRps, failRatio, userCount },
}: IRootState) => ({
  isDistributed,
  state,
  host,
  totalRps,
  failRatio,
  userCount,
  workerCount,
});

export default connect(storeConnector)(SwarmMonitor);
