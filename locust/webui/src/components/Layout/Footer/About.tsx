import { useState } from 'react';
import { Box, Button, Link, Typography } from '@mui/material';

import Modal from 'components/Modal/Modal';
import { useSelector } from 'redux/hooks';

export default function About() {
  const [open, setOpen] = useState(false);
  const version = useSelector(({ swarm }) => swarm.version);

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button color='inherit' onClick={() => setOpen(true)} variant='text'>
          About
        </Button>
      </Box>
      <Modal onClose={() => setOpen(false)} open={open}>
        <div>
          <Typography component='h2' mb={1} variant='h4'>
            About
          </Typography>
          <Typography component='p' variant='subtitle1'>
            Locust is free and open source software released under the{' '}
            <Link href={`https://github.com/locustio/locust/blob/master/LICENSE`}>MIT License</Link>
          </Typography>
          <Typography component='p' sx={{ mt: 2 }} variant='subtitle1'>
            It was originally developed by Carl Byström and{' '}
            <Link href={`https://twitter.com/jonatanheyman/`}>Jonatan Heyman</Link>. Since 2019, it
            is primarily maintained by <Link href={`https://github.com/cyberw`}>Lars Holmberg</Link>
            .
          </Typography>
          <Typography component='p' sx={{ mt: 2 }} variant='subtitle1'>
            Many thanks to all our wonderful{' '}
            <Link href={`https://github.com/locustio/locust/graphs/contributors`}>
              contributors
            </Link>
            !
          </Typography>
        </div>

        <div>
          <Typography component='h2' mb={1} variant='h4'>
            Version
          </Typography>
          <Link href={`https://github.com/locustio/locust/releases/tag/${version}`}>{version}</Link>
        </div>

        <div>
          <Typography component='h2' mb={1} variant='h4'>
            Links
          </Typography>
          <Typography component='p' variant='subtitle1'>
            <Link href='https://github.com/locustio/locust'>GitHub</Link>
          </Typography>
          <Typography component='p' variant='subtitle1'>
            <Link href='https://docs.locust.io/en/stable/'>Documentation</Link>
          </Typography>
        </div>
      </Modal>
    </>
  );
}
