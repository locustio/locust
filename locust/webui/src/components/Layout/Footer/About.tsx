import { useState } from 'react';
import { Box, Button, Link, Typography } from '@mui/material';

import Modal from 'components/Modal/Modal';
import { useSelector } from 'redux/hooks';

const authors = [
  {
    name: 'Carl Byström',
    website: 'http://cgbystrom.com/',
    social: { handle: '@cgbystrom', link: 'https://twitter.com/cgbystrom/' },
  },
  {
    name: 'Jonatan Heyman',
    website: 'http://heyman.info/',
    social: { handle: '@jonatanheyman', link: 'https://twitter.com/jonatanheyman/' },
  },
  { name: 'Joakim Hamrén', social: { handle: '@jahaaja', link: 'https://twitter.com/Jahaaja/' } },
  {
    name: 'ESN Social Software',
    website: 'http://esn.me/',
    social: { handle: '@uprise_ea', link: 'https://twitter.com/uprise_ea' },
  },
  {
    name: 'Hugo Heyman',
    social: { handle: '@hugoheyman', link: 'https://twitter.com/hugoheyman/' },
  },
  {
    name: 'Lars Holmberg',
    social: { handle: '@cyberw', link: 'https://github.com/cyberw' },
  },
];

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
            The original idea for Locust was Carl Byström's who made a first proof of concept in
            June 2010. Jonatan Heyman picked up Locust in January 2011, implemented the current
            concept of Locust classes and made it work distributed across multiple machines.
          </Typography>
          <Typography component='p' sx={{ mt: 2 }} variant='subtitle1'>
            Jonatan, Carl and Joakim Hamrén then continued the development of Locust at their job,
            ESN Social Software, who adopted Locust as an inhouse Open Source project.
          </Typography>
          <Typography component='p' sx={{ mt: 2 }} variant='subtitle1'>
            In 2019, the project changed ownership and has since been picked up and maintained by
            Lars Holmberg.
          </Typography>
          <Typography component='p' sx={{ mt: 2 }} variant='subtitle1'>
            Locust is now used by millions of users around the world and hundreds of developers
            contribute to its development.
          </Typography>
        </div>

        <div>
          <Typography component='h2' mb={1} variant='h4'>
            Authors and Copyright
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 0.5 }}>
            {authors.map(({ name, website, social: { handle, link } }, index) => (
              <div key={`author-${index}`}>
                {website ? <Link href={website}>{name}</Link> : name}
                <Box sx={{ display: 'inline', ml: 0.5 }}>
                  {'('}
                  <Link href={link}>{handle}</Link>
                  {')'}
                </Box>
              </div>
            ))}
          </Box>
        </div>

        <div>
          <Typography component='h2' mb={1} variant='h4'>
            License
          </Typography>
          <Typography component='p' variant='subtitle1'>
            Open source licensed under the MIT license.
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
            Website
          </Typography>
          <Link href='https://locust.io/'>https://locust.io</Link>
        </div>
      </Modal>
    </>
  );
}
