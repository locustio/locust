import { Box, Button, Container, TextField, Typography } from '@mui/material';
import { connect } from 'react-redux';

import Form from 'components/Form/Form';
import { useStartSwarmMutation } from 'redux/api/swarm';
import { ISwarmState, swarmActions } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';

type ISwarmFormInput = Pick<ISwarmState, 'spawnRate' | 'userCount'>;

interface ISwarmForm extends ISwarmFormInput {
  onSubmit: () => void;
  setSwarm: (swarmPayload: Partial<ISwarmState>) => void;
}

function SwarmEditForm({ onSubmit, userCount, spawnRate, setSwarm }: ISwarmForm) {
  const [startSwarm] = useStartSwarmMutation();

  const onEditSwarm = (inputData: ISwarmFormInput) => {
    onSubmit();
    startSwarm(inputData);
    setSwarm(inputData);
  };

  return (
    <Container maxWidth='md' sx={{ my: 2 }}>
      <Typography component='h2' noWrap variant='h6'>
        Edit running load test
      </Typography>
      <Form<ISwarmFormInput> onSubmit={onEditSwarm}>
        <Box sx={{ my: 2, display: 'flex', flexDirection: 'column', rowGap: 4 }}>
          <TextField
            defaultValue={userCount || 1}
            label='Number of users (peak concurrency)'
            name='userCount'
          />

          <TextField
            defaultValue={spawnRate || 1}
            label='Ramp up (users started/second)'
            name='spawnRate'
          />

          <Button size='large' type='submit' variant='contained'>
            Update
          </Button>
        </Box>
      </Form>
    </Container>
  );
}

const storeConnector = ({ swarm: { spawnRate, userCount } }: IRootState) => ({
  spawnRate,
  userCount,
});

const actionCreator = {
  setSwarm: swarmActions.setSwarm,
};

export default connect(storeConnector, actionCreator)(SwarmEditForm);
