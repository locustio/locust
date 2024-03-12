import { AppBar, Box, Container, Link, Toolbar, Typography } from '@mui/material';

import DarkLightToggle from 'components/Layout/Navbar/DarkLightToggle';
import SwarmMonitor from 'components/Layout/Navbar/SwarmMonitor';
import StateButtons from 'components/StateButtons/StateButtons';

export default function Navbar() {
  return (
    <AppBar position='static'>
      <Container maxWidth='xl'>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Link
            color='inherit'
            href='/'
            sx={{ display: 'flex', alignItems: 'center', columnGap: 2 }}
            underline='none'
          >
            <img height='52' src='./assets/logo.png' width='52' />
            <Typography
              component='h1'
              noWrap
              sx={{
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
              }}
              variant='h3'
            >
              Locust
            </Typography>
          </Link>
          <Box sx={{ display: 'flex', columnGap: 6 }}>
            <SwarmMonitor />
            <StateButtons />
            <DarkLightToggle />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
