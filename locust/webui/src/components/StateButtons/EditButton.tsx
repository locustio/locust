import { useState } from 'react';
import { Button } from '@mui/material';

import Modal from 'components/Modal/Modal';
import SwarmForm, { ISwarmFormProps } from 'components/SwarmForm/SwarmForm';

export default function EditButton(swarmFormProps: ISwarmFormProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button color='secondary' onClick={() => setOpen(true)} type='button' variant='contained'>
        Edit
      </Button>
      <Modal onClose={() => setOpen(false)} open={open}>
        <SwarmForm {...swarmFormProps} isEditSwarm onFormSubmit={() => setOpen(false)} />
      </Modal>
    </>
  );
}
