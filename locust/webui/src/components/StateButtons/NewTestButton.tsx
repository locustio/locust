import { useState } from 'react';
import { Button } from '@mui/material';

import Modal from 'components/Modal/Modal';
import SwarmForm, { ISwarmFormProps } from 'components/SwarmForm/SwarmForm';

export default function NewTestButton(swarmFormProps: ISwarmFormProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button color='success' onClick={() => setOpen(true)} type='button' variant='contained'>
        New
      </Button>
      <Modal onClose={() => setOpen(false)} open={open}>
        <SwarmForm {...swarmFormProps} />
      </Modal>
    </>
  );
}
