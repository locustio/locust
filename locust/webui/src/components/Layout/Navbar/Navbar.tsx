import { useEffect, useState } from 'react';
import MenuIcon from '@mui/icons-material/Menu';
import { AppBar, Box, Container, Drawer, IconButton, Link, Toolbar, useTheme } from '@mui/material';

import Logo from 'assets/Logo';
import DarkLightToggle from 'components/Layout/Navbar/DarkLightToggle';
import SwarmMonitor from 'components/Layout/Navbar/SwarmMonitor';
import StateButtons from 'components/StateButtons/StateButtons';

export default function Navbar() {
  const theme = useTheme();
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= theme.breakpoints.values.md) {
        setDrawerOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const toggleDrawer = (open: boolean) => () => {
    setDrawerOpen(open);
  };

  return (
    <>
      <AppBar position='static'>
        <Container maxWidth='xl'>
          <Toolbar
            disableGutters
            sx={{ display: 'flex', justifyContent: 'space-between', columnGap: 2 }}
          >
            <Link
              color='inherit'
              href='/'
              sx={{ display: 'flex', alignItems: 'center' }}
              underline='none'
            >
              <Logo />
            </Link>
            <IconButton
              aria-label='menu'
              color='inherit'
              edge='start'
              onClick={toggleDrawer(true)}
              sx={{ display: { xs: 'block', md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>

            <Box sx={{ display: { xs: 'none', md: 'flex' }, columnGap: { md: 2, lg: 6 } }}>
              <SwarmMonitor />
              <StateButtons />
              <DarkLightToggle />
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      <Drawer anchor='right' onClose={toggleDrawer(false)} open={drawerOpen}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            columnGap: { md: 2, lg: 6 },
            rowGap: 2,
            p: 2,
            maxWidth: '100vw',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <DarkLightToggle />
          </Box>
          <StateButtons />
          <SwarmMonitor />
        </Box>
      </Drawer>
    </>
  );
}
