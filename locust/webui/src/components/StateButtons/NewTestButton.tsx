import { useState } from 'react';
import { Button } from '@mui/material';

import Modal from 'components/Modal/Modal';
import SwarmForm from 'components/SwarmForm/SwarmForm';

export default function NewTestButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button color='success' onClick={() => setOpen(true)} type='button' variant='contained'>
        New
      </Button>
      <Modal onClose={() => setOpen(false)} open={open}>
        <SwarmForm />
      </Modal>
    </>
  );
}
