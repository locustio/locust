import { ReactNode } from 'react';

import Footer from 'components/Layout/Footer/Footer';
import Navbar from 'components/Layout/Navbar/Navbar';

interface ILayout {
  children: ReactNode;
}

export default function Layout({ children }: ILayout) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      <Footer />
    </>
  );
}
