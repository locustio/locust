import { useState } from 'react';
import { Button } from '@mui/material';

import Modal from 'components/Modal/Modal';
import SwarmEditForm from 'components/SwarmForm/SwarmEditForm';

export default function EditButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button color='secondary' onClick={() => setOpen(true)} type='button' variant='contained'>
        Edit
      </Button>
      <Modal onClose={() => setOpen(false)} open={open}>
        <SwarmEditForm onSubmit={() => setOpen(false)} />
      </Modal>
    </>
  );
}
