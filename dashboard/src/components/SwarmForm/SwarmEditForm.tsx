import { Box, Button, Container, TextField, Typography } from '@mui/material';
import { connect } from 'react-redux';

import { asyncRequest, REQUEST_METHODS } from 'api/asyncRequest';
import Form from 'components/Form/Form';
import { ISwarmState } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';

type ISwarmFormInput = Pick<ISwarmState, 'spawnRate' | 'userCount'>;

interface ISwarmForm extends ISwarmFormInput {
  onSubmit: () => void;
}

function SwarmEditForm({ onSubmit, spawnRate, userCount }: ISwarmForm) {
  const onEditSwarm = (inputData: ISwarmFormInput) => {
    onSubmit();
    asyncRequest('swarm', {
      method: REQUEST_METHODS.POST,
      body: inputData,
      form: true,
    });
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
            label='Ramp Up (users started/second)'
            name='spawnRate'
          />

          <Button size='large' type='submit' variant='contained'>
            Update Swarm
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

export default connect(storeConnector)(SwarmEditForm);
