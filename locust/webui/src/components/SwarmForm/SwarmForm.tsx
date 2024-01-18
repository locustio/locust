import { useState } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  Container,
  TextField,
  Typography,
} from '@mui/material';
import { connect } from 'react-redux';

import Form from 'components/Form/Form';
import Select from 'components/Form/Select';
import CustomParameters from 'components/SwarmForm/SwarmCustomParameters';
import SwarmUserClassPicker from 'components/SwarmForm/SwarmUserClassPicker';
import { SWARM_STATE } from 'constants/swarm';
import { useStartSwarmMutation } from 'redux/api/swarm';
import { swarmActions, ISwarmState } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';
import { isEmpty } from 'utils/object';

interface ISwarmFormInput extends Pick<ISwarmState, 'host' | 'spawnRate' | 'userCount'> {
  runTime: string;
  userClasses: string[];
  shapeClass: string;
}

interface IDispatchProps {
  setSwarm: (swarmPayload: Partial<ISwarmState>) => void;
}

interface ISwarmForm
  extends IDispatchProps,
    Pick<
      ISwarmState,
      | 'availableShapeClasses'
      | 'availableUserClasses'
      | 'extraOptions'
      | 'isShape'
      | 'host'
      | 'overrideHostWarning'
      | 'runTime'
      | 'showUserclassPicker'
      | 'spawnRate'
      | 'numUsers'
    > {}

function SwarmForm({
  availableShapeClasses,
  availableUserClasses,
  host,
  extraOptions,
  isShape,
  numUsers,
  overrideHostWarning,
  runTime,
  setSwarm,
  showUserclassPicker,
  spawnRate,
}: ISwarmForm) {
  const [startSwarm] = useStartSwarmMutation();
  const [selectedUserClasses, setSelectedUserClasses] = useState(availableUserClasses);

  const onStartSwarm = (inputData: ISwarmFormInput) => {
    setSwarm({
      state: SWARM_STATE.RUNNING,
      host: inputData.host || host,
      runTime: inputData.runTime,
      spawnRate: Number(inputData.spawnRate) || null,
      numUsers: Number(inputData.userCount) || null,
    });

    startSwarm({
      ...inputData,
      ...(showUserclassPicker && selectedUserClasses ? { userClasses: selectedUserClasses } : {}),
    });
  };

  return (
    <Container maxWidth='md' sx={{ my: 2 }}>
      <Typography component='h2' noWrap variant='h6'>
        Start new load test
      </Typography>
      {showUserclassPicker && (
        <Box marginBottom={2} marginTop={2}>
          <SwarmUserClassPicker
            selectedUserClasses={selectedUserClasses}
            setSelectedUserClasses={setSelectedUserClasses}
          />
        </Box>
      )}
      <Form<ISwarmFormInput> onSubmit={onStartSwarm}>
        <Box
          sx={{
            marginBottom: 2,
            marginTop: 2,
            display: 'flex',
            flexDirection: 'column',
            rowGap: 4,
          }}
        >
          {showUserclassPicker && (
            <Select label='Shape Class' name='shapeClass' options={availableShapeClasses} />
          )}
          <TextField
            defaultValue={(isShape && '-') || numUsers || 1}
            disabled={!!isShape}
            label='Number of users (peak concurrency)'
            name='userCount'
          />
          <TextField
            defaultValue={(isShape && '-') || spawnRate || 1}
            disabled={!!isShape}
            label='Ramp Up (users started/second)'
            name='spawnRate'
            title='Disabled for tests using LoadTestShape class'
          />
          <TextField
            defaultValue={host}
            label={`Host ${
              overrideHostWarning
                ? '(setting this will override the host for the User classes)'
                : ''
            }`}
            name='host'
            title='Disabled for tests using LoadTestShape class'
          />
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Advanced options</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TextField
                defaultValue={runTime}
                label='Run time (e.g. 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.)'
                name='runTime'
                sx={{ width: '100%' }}
              />
            </AccordionDetails>
          </Accordion>
          {!isEmpty(extraOptions) && <CustomParameters extraOptions={extraOptions} />}
          <Button size='large' type='submit' variant='contained'>
            Start Swarm
          </Button>
        </Box>
      </Form>
    </Container>
  );
}

const storeConnector = ({
  swarm: {
    availableShapeClasses,
    availableUserClasses,
    extraOptions,
    isShape,
    host,
    numUsers,
    overrideHostWarning,
    runTime,
    spawnRate,
    showUserclassPicker,
  },
}: IRootState) => ({
  availableShapeClasses,
  availableUserClasses,
  extraOptions,
  isShape,
  host,
  overrideHostWarning,
  showUserclassPicker,
  numUsers,
  runTime,
  spawnRate,
});

const actionCreator: IDispatchProps = {
  setSwarm: swarmActions.setSwarm,
};

export default connect(storeConnector, actionCreator)(SwarmForm);
