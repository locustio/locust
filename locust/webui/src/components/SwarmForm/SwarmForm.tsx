import { useMemo, useState } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Autocomplete,
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
import { useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';
import { ICustomInput } from 'types/form.types';
import { ISwarmFormInput, ISwarmState } from 'types/swarm.types';
import { isEmpty } from 'utils/object';

interface IDispatchProps {
  setSwarm: (swarmPayload: Partial<ISwarmState>) => void;
}

interface IAdvancedOptions extends ICustomInput {
  component?: React.ElementType;
}

export interface ISwarmFormProps extends Pick<ISwarmState, 'allProfiles'> {
  alert?: {
    level?: AlertColor;
    message: string;
  };
  isDisabled?: boolean;
  isEditSwarm?: boolean;
  onFormChange?: (formData: React.ChangeEvent<HTMLFormElement>) => void;
  onFormSubmit?: (inputData: ISwarmFormInput) => void;
  advancedOptions?: IAdvancedOptions[];
}

interface ISwarmForm
  extends IDispatchProps,
    Pick<
      ISwarmState,
      | 'allProfiles'
      | 'availableShapeClasses'
      | 'availableUserClasses'
      | 'extraOptions'
      | 'hideCommonOptions'
      | 'shapeUseCommonOptions'
      | 'host'
      | 'overrideHostWarning'
      | 'profile'
      | 'runTime'
      | 'showUserclassPicker'
      | 'spawnRate'
      | 'numUsers'
      | 'userCount'
    >,
    ISwarmFormProps {}

interface ICanSubmitForm extends ISwarmState {
  isDisabled?: boolean;
}

const canSubmitSwarmForm = ({
  isDisabled,
  isDistributed,
  workerCount,
}: ICanSubmitForm): { isFormDisabled?: boolean; reason?: string } => {
  if (isDisabled) {
    return { isFormDisabled: true };
  }

  if (isDistributed && !workerCount) {
    return {
      isFormDisabled: true,
      reason:
        "You can't start a distributed test before at least one worker processes has connected",
    };
  }

  return {};
};

function SwarmForm({
  allProfiles,
  availableShapeClasses,
  availableUserClasses,
  host,
  extraOptions,
  hideCommonOptions,
  shapeUseCommonOptions,
  numUsers,
  userCount,
  overrideHostWarning,
  profile,
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
  const swarm = useSelector(({ swarm }) => swarm);

  const { reason: formDisabledReason, isFormDisabled } = useMemo(
    () => canSubmitSwarmForm({ isDisabled, ...swarm }),
    [isDisabled, swarm],
  );

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
        profile: inputData.profile,
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
                  <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4 }}>
                    <TextField
                      defaultValue={runTime}
                      disabled={!!hideCommonOptions}
                      label='Run time (e.g. 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.)'
                      name='runTime'
                      sx={{ width: '100%' }}
                      title={
                        hideCommonOptions ? 'Disabled for tests using LoadTestShape class' : ''
                      }
                    />
                    <Autocomplete
                      defaultValue={profile}
                      disablePortal
                      freeSolo
                      options={allProfiles && Array.isArray(allProfiles) ? allProfiles : []}
                      renderInput={params => (
                        <TextField
                          {...params}
                          defaultValue={profile}
                          label='Profile'
                          name='profile'
                        />
                      )}
                    />
                    {advancedOptions &&
                      advancedOptions.map(({ component: Component, ...inputProps }, index) =>
                        Component ? (
                          <Component {...inputProps} />
                        ) : (
                          <CustomInput {...inputProps} key={`advanced-parameter-${index}`} />
                        ),
                      )}
                  </Box>
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
          {(errorMessage || formDisabledReason) && (
            <Alert severity={'error'}>{errorMessage || formDisabledReason}</Alert>
          )}
          <Button disabled={isFormDisabled} size='large' type='submit' variant='contained'>
            {isEditSwarm ? 'Update' : 'Start'}
          </Button>
        </Box>
      </Form>
    </Container>
  );
}

const storeConnector = (
  {
    swarm: {
      allProfiles,
      availableShapeClasses,
      availableUserClasses,
      extraOptions,
      hideCommonOptions,
      shapeUseCommonOptions,
      host,
      numUsers,
      userCount,
      overrideHostWarning,
      profile,
      runTime,
      spawnRate,
      showUserclassPicker,
    },
  }: IRootState,
  ownProps?: ISwarmFormProps,
) => ({
  allProfiles: allProfiles || ownProps?.allProfiles,
  availableShapeClasses,
  availableUserClasses,
  extraOptions,
  hideCommonOptions,
  shapeUseCommonOptions,
  host,
  overrideHostWarning,
  profile,
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
