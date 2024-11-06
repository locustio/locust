import { useState } from 'react';
import { Box, Button, Tooltip } from '@mui/material';

import Modal from 'components/Modal/Modal';
import SwarmForm, { ISwarmFormProps } from 'components/SwarmForm/SwarmForm';
import { useSelector } from 'redux/hooks';

export default function EditButton(swarmFormProps: ISwarmFormProps) {
  const [open, setOpen] = useState(false);
  const { hideCommonOptions } = useSelector(({ swarm }) => swarm);

  return (
    <>
      <Tooltip title={hideCommonOptions ? 'Disabled for tests using LoadTestShape class' : ''}>
        <Box>
          <Button
            color='secondary'
            disabled={!!hideCommonOptions}
            onClick={() => setOpen(true)}
            sx={{ minHeight: '100%' }}
            type='button'
            variant='contained'
          >
            Edit
          </Button>
        </Box>
      </Tooltip>
      <Modal onClose={() => setOpen(false)} open={open}>
        <SwarmForm {...swarmFormProps} isEditSwarm onFormSubmit={() => setOpen(false)} />
      </Modal>
    </>
  );
}
