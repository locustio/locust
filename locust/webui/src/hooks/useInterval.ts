import { useEffect, useRef } from 'react';

export default function useInterval(
  callback: () => void,
  delay: number,
  { shouldRunInterval, immediate }: { shouldRunInterval?: boolean; immediate?: boolean } = {
    shouldRunInterval: true,
    immediate: false,
  },
) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!shouldRunInterval) {
      return;
    }

    if (immediate) {
      savedCallback.current();
    }

    const interval = setInterval(() => savedCallback.current(), delay);

    return () => {
      clearInterval(interval);
    };
  }, [delay, shouldRunInterval]);
}
