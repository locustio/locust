import { useState } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Container,
  SelectChangeEvent,
  TextField,
  Typography,
} from '@mui/material';
import { AlertColor } from '@mui/material/Alert';
import { connect } from 'react-redux';

import CustomInput from 'components/Form/CustomInput';
import Form from 'components/Form/Form';
import NumericField from 'components/Form/NumericField';
import Select from 'components/Form/Select';
import CustomParameters from 'components/SwarmForm/SwarmCustomParameters';
import SwarmUserClassPicker from 'components/SwarmForm/SwarmUserClassPicker';
import { SWARM_STATE } from 'constants/swarm';
import { useStartSwarmMutation } from 'redux/api/swarm';
import { swarmActions } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';
import { ICustomInput } from 'types/form.types';
import { ISwarmFormInput, ISwarmState } from 'types/swarm.types';
import { isEmpty } from 'utils/object';

interface IDispatchProps {
  setSwarm: (swarmPayload: Partial<ISwarmState>) => void;
}

export interface ISwarmFormProps {
  alert?: {
    level?: AlertColor;
    message: string;
  };
  isDisabled?: boolean;
  isEditSwarm?: boolean;
  onFormChange?: (formData: React.ChangeEvent<HTMLFormElement>) => void;
  onFormSubmit?: (inputData: ISwarmFormInput) => void;
  advancedOptions?: ICustomInput[];
}

interface ISwarmForm
  extends IDispatchProps,
    Pick<
      ISwarmState,
      | 'availableShapeClasses'
      | 'availableUserClasses'
      | 'extraOptions'
      | 'hideCommonOptions'
      | 'shapeUseCommonOptions'
      | 'host'
      | 'overrideHostWarning'
      | 'runTime'
      | 'showUserclassPicker'
      | 'spawnRate'
      | 'numUsers'
      | 'userCount'
    >,
    ISwarmFormProps {}

function SwarmForm({
  availableShapeClasses,
  availableUserClasses,
  host,
  extraOptions,
  hideCommonOptions,
  shapeUseCommonOptions,
  numUsers,
  userCount,
  overrideHostWarning,
  runTime,
  setSwarm,
  showUserclassPicker,
  spawnRate,
  alert,
  isDisabled = false,
  isEditSwarm = false,
  onFormChange,
  onFormSubmit,
  advancedOptions,
}: ISwarmForm) {
  const [startSwarm] = useStartSwarmMutation();
  const [errorMessage, setErrorMessage] = useState('');
  const [selectedUserClasses, setSelectedUserClasses] = useState(availableUserClasses);

  const onStartSwarm = async (inputData: ISwarmFormInput) => {
    const { data } = await startSwarm({
      ...inputData,
      ...(showUserclassPicker && selectedUserClasses ? { userClasses: selectedUserClasses } : {}),
    });

    if (data && data.success) {
      setSwarm({
        state: SWARM_STATE.RUNNING,
        host: inputData.host || host,
        runTime: inputData.runTime,
        spawnRate: inputData.spawnRate,
        userCount: inputData.userCount,
      });
    } else {
      setErrorMessage(data ? data.message : 'An unknown error occured.');
    }

    if (onFormSubmit) {
      onFormSubmit(inputData);
    }
  };

  const handleSwarmFormChange = (formEvent: React.ChangeEvent<HTMLFormElement>) => {
    if (errorMessage) {
      setErrorMessage('');
    }

    if (onFormChange) {
      onFormChange(formEvent);
    }
  };

  const onShapeClassChange = (event: SelectChangeEvent<unknown>) => {
    if (!shapeUseCommonOptions) {
      const hasSelectedShapeClass = event.target.value !== availableShapeClasses[0];
      setSwarm({
        hideCommonOptions: hasSelectedShapeClass,
      });
    }
  };

  return (
    <Container maxWidth='md' sx={{ my: 2 }}>
      <Typography component='h2' noWrap variant='h6'>
        {isEditSwarm ? 'Edit running load test' : 'Start new load test'}
      </Typography>
      {!isEditSwarm && showUserclassPicker && (
        <Box marginBottom={2} marginTop={2}>
          <SwarmUserClassPicker
            availableUserClasses={availableUserClasses}
            selectedUserClasses={selectedUserClasses}
            setSelectedUserClasses={setSelectedUserClasses}
          />
        </Box>
      )}
      <Form<ISwarmFormInput> onChange={handleSwarmFormChange} onSubmit={onStartSwarm}>
        <Box
          sx={{
            marginBottom: 2,
            marginTop: 2,
            display: 'flex',
            flexDirection: 'column',
            rowGap: 4,
          }}
        >
          {!isEditSwarm && showUserclassPicker && (
            <Select
              label='Shape Class'
              name='shapeClass'
              onChange={onShapeClassChange}
              options={availableShapeClasses}
            />
          )}
          <NumericField
            defaultValue={(hideCommonOptions && '0') || userCount || numUsers || 1}
            disabled={!!hideCommonOptions}
            label='Number of users (peak concurrency)'
            name='userCount'
            required
            title={hideCommonOptions ? 'Disabled for tests using LoadTestShape class' : ''}
          />
          <NumericField
            defaultValue={(hideCommonOptions && '0') || spawnRate || 1}
            disabled={!!hideCommonOptions}
            label='Ramp up (users started/second)'
            name='spawnRate'
            required
            title={hideCommonOptions ? 'Disabled for tests using LoadTestShape class' : ''}
          />
          {!isEditSwarm && (
            <>
              <TextField
                defaultValue={host}
                label={`Host ${
                  overrideHostWarning
                    ? '(setting this will override the host for the User classes)'
                    : ''
                }`}
                name='host'
              />
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Advanced options</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    defaultValue={runTime}
                    disabled={!!hideCommonOptions}
                    label='Run time (e.g. 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.)'
                    name='runTime'
                    sx={{ width: '100%' }}
                    title={hideCommonOptions ? 'Disabled for tests using LoadTestShape class' : ''}
                  />
                  {advancedOptions && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4, mt: 4 }}>
                      {advancedOptions.map((inputProps, index) => (
                        <CustomInput {...inputProps} key={`advanced-parameter-${index}`} />
                      ))}
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            </>
          )}
          {!!extraOptions && !isEmpty(extraOptions) && (
            <CustomParameters extraOptions={extraOptions} />
          )}
          {alert && !errorMessage && (
            <Alert severity={alert.level || 'info'}>{alert.message}</Alert>
          )}
          {errorMessage && <Alert severity={'error'}>{errorMessage}</Alert>}
          <Button disabled={isDisabled} size='large' type='submit' variant='contained'>
            {isEditSwarm ? 'Update' : 'Start'}
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
    hideCommonOptions,
    shapeUseCommonOptions,
    host,
    numUsers,
    userCount,
    overrideHostWarning,
    runTime,
    spawnRate,
    showUserclassPicker,
  },
}: IRootState) => ({
  availableShapeClasses,
  availableUserClasses,
  extraOptions,
  hideCommonOptions,
  shapeUseCommonOptions,
  host,
  overrideHostWarning,
  showUserclassPicker,
  numUsers,
  userCount,
  runTime,
  spawnRate,
});

const actionCreator: IDispatchProps = {
  setSwarm: swarmActions.setSwarm,
};

export default connect(storeConnector, actionCreator)(SwarmForm);
