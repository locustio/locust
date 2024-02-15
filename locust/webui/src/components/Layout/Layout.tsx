import { ReactNode } from 'react';
import { Box } from '@mui/material';

import Footer from 'components/Layout/Footer/Footer';
import Navbar from 'components/Layout/Navbar/Navbar';

interface ILayout {
  children: ReactNode;
}

export default function Layout({ children }: ILayout) {
  return (
    <>
      <Box sx={{ minHeight: 'calc(100vh - var(--footer-height))' }}>
        <Navbar />
        <main>{children}</main>
      </Box>
      <Footer />
    </>
  );
}
