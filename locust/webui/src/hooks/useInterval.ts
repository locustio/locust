import { useEffect, useRef } from 'react';

export default function useInterval(
  callback: () => void,
  delay: number,
  { shouldRunInterval } = { shouldRunInterval: true },
) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!shouldRunInterval) {
      return;
    }

    const interval = setInterval(() => savedCallback.current(), delay);

    return () => {
      clearInterval(interval);
    };
  }, [delay, shouldRunInterval]);
}
