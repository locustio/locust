import { Container } from '@mui/material';

import About from 'components/Layout/Footer/About';

export default function Footer() {
  return (
    <Container
      maxWidth='xl'
      sx={{
        display: 'flex',
        height: 'var(--footer-height)',
        alignItems: 'center',
        justifyContent: 'flex-end',
      }}
    >
      <About />
    </Container>
  );
}
