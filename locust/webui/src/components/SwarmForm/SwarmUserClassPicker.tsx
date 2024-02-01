import { useState } from 'react';
import SettingsIcon from '@mui/icons-material/Settings';
import {
  Box,
  Button,
  Checkbox,
  FormGroup,
  IconButton,
  InputLabel,
  TableCell,
  TextField,
  Typography,
  Table,
  TableRow,
  TableBody,
  TableContainer,
  Paper,
} from '@mui/material';
import { connect } from 'react-redux';

import Form from 'components/Form/Form';
import Select from 'components/Form/Select';
import Modal from 'components/Modal/Modal';
import { useUpdateUserSettingsMutation } from 'redux/api/swarm';
import { ISwarmState, swarmActions } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';
import { ISwarmUser } from 'types/swarm.types';
import { toTitleCase } from 'utils/string';

interface IDispatchProps {
  setSwarm: (swarmPayload: Partial<ISwarmState>) => void;
}

interface IUserClassPicker
  extends IDispatchProps,
    Pick<ISwarmState, 'availableUserTasks' | 'users'> {
  selectedUserClasses: string[];
  setSelectedUserClasses: (userClasses: string[]) => void;
}

interface IUserToEdit {
  userClassName: string;
  userClass: ISwarmUser;
}

interface ISwarmUserForm {
  availableTasks: string[];
  userToEdit: IUserToEdit;
  handleEditUser: (updatedUser: ISwarmUser) => void;
}

function SwarmUserForm({ availableTasks, userToEdit, handleEditUser }: ISwarmUserForm) {
  const { tasks, ...userFieldsToEdit } = userToEdit.userClass;

  return (
    <Form onSubmit={handleEditUser}>
      <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4, my: 2 }}>
        <Typography>{`${userToEdit.userClassName} Settings`}</Typography>
        <Select defaultValue={tasks} label='Tasks' multiple name='tasks' options={availableTasks} />
        {Object.entries(userFieldsToEdit).map(([field, value]) => (
          <TextField
            defaultValue={value}
            inputProps={{ 'data-type': typeof value === 'number' ? 'number' : 'text' }}
            key={`user-to-edit-${field}`}
            label={toTitleCase(field)}
            name={field}
          />
        ))}

        <Button size='large' type='submit' variant='contained'>
          Save
        </Button>
      </Box>
    </Form>
  );
}

function SwarmUserClassPicker({
  availableUserTasks,
  selectedUserClasses,
  setSelectedUserClasses,
  setSwarm,
  users,
}: IUserClassPicker) {
  const [open, setOpen] = useState(false);
  const [userToEdit, setUserToEdit] = useState<IUserToEdit>();

  const [updateUserSettings] = useUpdateUserSettingsMutation();

  const handleEditUser = (updatedUser: ISwarmUser) => {
    if (userToEdit) {
      setSwarm({
        users: {
          ...users,
          [userToEdit.userClassName]: updatedUser,
        },
      });
      updateUserSettings({ ...updatedUser, userClassName: userToEdit.userClassName });
      setOpen(false);
    }
  };

  const handleToggleUserSelected = (name: string) => () =>
    selectedUserClasses.includes(name)
      ? setSelectedUserClasses(selectedUserClasses.filter(n => n !== name))
      : setSelectedUserClasses(selectedUserClasses.concat(name));

  return (
    <>
      <Box
        sx={{
          position: 'relative',
          border: '1px',
          borderColor: 'divider',
          borderStyle: 'solid',
          padding: 2,
          borderRadius: 1,
        }}
      >
        <Box
          sx={{
            maxHeight: '30vh',
            overflow: 'auto',
          }}
        >
          <InputLabel
            shrink
            sx={{
              position: 'absolute',
              backgroundColor: 'background.paper',
              width: 'fit-content',
              top: '0',
              marginTop: '-5px',
              padding: '0 5px',
            }}
          >
            User Classes
          </InputLabel>
          <FormGroup>
            <TableContainer component={Paper}>
              <Table>
                <TableBody>
                  {Object.entries(users).map(([name, userClass]) => (
                    <TableRow hover key={`user-class-${name}`}>
                      <TableCell onClick={handleToggleUserSelected(name)} padding='checkbox'>
                        <Checkbox defaultChecked />
                      </TableCell>

                      <TableCell>{name}</TableCell>
                      <TableCell>
                        <Typography variant='subtitle2'>{userClass.host}</Typography>
                      </TableCell>
                      <TableCell align='right'>
                        <IconButton
                          onClick={() => {
                            setOpen(!open);
                            setUserToEdit({ userClass, userClassName: name });
                          }}
                        >
                          <SettingsIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </FormGroup>
        </Box>
      </Box>
      <Modal onClose={() => setOpen(false)} open={open}>
        {userToEdit && (
          <SwarmUserForm
            availableTasks={availableUserTasks[userToEdit.userClassName]}
            handleEditUser={handleEditUser}
            userToEdit={userToEdit}
          />
        )}
      </Modal>
    </>
  );
}

const actionCreator: IDispatchProps = {
  setSwarm: swarmActions.setSwarm,
};

const storeConnector = ({ swarm: { availableUserTasks, users } }: IRootState) => ({
  availableUserTasks,
  users,
});

export default connect(storeConnector, actionCreator)(SwarmUserClassPicker);
