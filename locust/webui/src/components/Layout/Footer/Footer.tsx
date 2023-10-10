import { Box, Container } from '@mui/material';

import About from 'components/Layout/Footer/About';

export default function Footer() {
  return (
    <Box component='nav' sx={{ position: 'fixed', bottom: 0, width: '100%' }}>
      <Container maxWidth='xl' sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <About />
      </Container>
    </Box>
  );
}
