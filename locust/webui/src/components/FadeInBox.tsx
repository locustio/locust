import React, { useState, useEffect, useRef } from 'react';
import { Box, SxProps } from '@mui/material';

const threshold = 0.5;

const useFadeInOnScroll = () => {
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      {
        threshold,
      },
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, [threshold]);

  return { isVisible, elementRef };
};

export default function FadeInBox({ children, sx }: { children: React.ReactNode; sx?: SxProps }) {
  const { isVisible, elementRef } = useFadeInOnScroll();

  return (
    <Box
      ref={elementRef}
      sx={{ ...sx, opacity: isVisible ? 1 : 0, transition: 'opacity 1s ease-out' }}
    >
      {children}
    </Box>
  );
}
