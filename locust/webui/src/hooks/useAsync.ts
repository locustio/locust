import { useState, useEffect, useCallback } from 'react';

function useAsync<
  AsyncFunction extends (...args: any) => any = () => Promise<void>,
  AsyncFunctionReturn = void,
  AsyncFunctionError = ReturnType<typeof Error>,
>(asyncFunction: AsyncFunction, { execute: shouldExecuteImmediately = false } = {}) {
  const [isLoading, setIsLoading] = useState(true);
  const [value, setValue] = useState<AsyncFunctionReturn | null>(null);
  const [error, setError] = useState<AsyncFunctionError | null>(null);

  const execute = useCallback(
    (...args: Parameters<AsyncFunction>[] | []) => {
      setValue(null);
      setError(null);

      return asyncFunction(...args)
        .then((response: AsyncFunctionReturn) => {
          setValue(response);
          setIsLoading(false);
        })
        .catch((newError: AsyncFunctionError) => {
          setError(newError);
          setIsLoading(false);
        });
    },
    [asyncFunction],
  );

  useEffect(() => {
    if (shouldExecuteImmediately) {
      execute();
    }
  }, [execute, shouldExecuteImmediately]);

  return { execute, isLoading, value, error };
}

export default useAsync;
