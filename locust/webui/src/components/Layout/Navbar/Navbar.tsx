import { AppBar, Box, Container, Link, Toolbar } from '@mui/material';

import Logo from 'assets/Logo';
import DarkLightToggle from 'components/Layout/Navbar/DarkLightToggle';
import SwarmMonitor from 'components/Layout/Navbar/SwarmMonitor';
import StateButtons from 'components/StateButtons/StateButtons';
import { useSelector } from 'redux/hooks';

export default function Navbar() {
  const isDarkMode = useSelector(({ theme }) => theme.isDarkMode);

  return (
    <AppBar position='static'>
      <Container maxWidth='xl'>
        <Toolbar disableGutters sx={{ display: 'flex', justifyContent: 'space-between', columnGap: 2 }}>
          <Link
            color='inherit'
            href='/'
            sx={{ display: 'flex', alignItems: 'center' }}
            underline='none'
          >
            <Logo isDarkMode={isDarkMode} />
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
