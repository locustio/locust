import { Container } from '@mui/material';

import About from 'components/Layout/Footer/About';
import FeedbackForm from 'components/Layout/Footer/FeedbackForm';

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
      <FeedbackForm />
    </Container>
  );
}
