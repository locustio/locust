import { Box, Divider, Link, Tooltip, Typography } from '@mui/material';
import { connect } from 'react-redux';

import { SWARM_STATE } from 'constants/swarm';
import { IUiState, uiActions } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';
import { ISwarmState } from 'types/swarm.types';

interface ISwarmMonitor
  extends Pick<ISwarmState, 'isDistributed' | 'host' | 'state' | 'workerCount'>,
  Pick<IUiState, 'totalRps' | 'failRatio' | 'userCount'> { }
interface IActionProps {
  setUi: (payload: Partial<IUiState>) => void;
}

function SwarmMonitor({
  isDistributed,
  state,
  host,
  totalRps,
  failRatio,
  userCount,
  workerCount,
  setUi,
}: ISwarmMonitor & IActionProps) {
  const onTestClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setUi({ showTestTab: true });
  };

  return (
    <Box
      sx={{ display: 'flex', columnGap: 2, rowGap: 1, flexDirection: { xs: 'column', md: 'row' } }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
        <Typography sx={{ fontWeight: 'bold' }}>Host</Typography>
        <Tooltip title={host}>
          <Typography
            noWrap
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',

              maxWidth: { xs: '180px', lg: '400px' },
            }}
          >
            {host}
          </Typography>
        </Tooltip>
      </Box>
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
        <Typography sx={{ fontWeight: 'bold' }}>Status</Typography>
        <Typography variant='button'>{state}</Typography>
      </Box>
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: { md: 'center' } }}>
        <Link
          component='button'
          type='button'
          onClick={onTestClick}
          sx={{ color: 'inherit', fontWeight: 'bold', textDecoration: 'none', backgroundColor: '#e68508', padding: '4px 8px', borderRadius: '4px' }}
        >
          Run Test
        </Link>
      </Box>
      {(state === SWARM_STATE.RUNNING || state === SWARM_STATE.SPAWNING) && (
        <>
          <Divider flexItem orientation='vertical' />
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: { md: 'center' } }}>
            <Typography sx={{ fontWeight: 'bold' }}>Users</Typography>
            <Typography noWrap variant='button'>
              {userCount}
            </Typography>
          </Box>
        </>
      )}
      {isDistributed && (
        <>
          <Divider flexItem orientation='vertical' />
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: { md: 'center' } }}>
            <Typography sx={{ fontWeight: 'bold' }}>Workers</Typography>
            <Typography noWrap variant='button'>
              {workerCount}
            </Typography>
          </Box>
        </>
      )}
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: { md: 'center' } }}>
        <Typography sx={{ fontWeight: 'bold' }}>RPS</Typography>
        <Typography noWrap variant='button'>
          {totalRps}
        </Typography>
      </Box>
      <Divider flexItem orientation='vertical' />
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: { md: 'center' } }}>
        <Typography sx={{ fontWeight: 'bold' }}>Failures</Typography>
        <Typography noWrap variant='button'>{`${failRatio}%`}</Typography>
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

const actionCreator = {
  setUi: uiActions.setUi,
};

export default connect(storeConnector, actionCreator)(SwarmMonitor);
