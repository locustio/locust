import { useCallback } from 'react';
import { Dispatch, ActionCreator } from '@reduxjs/toolkit';
import {
  TypedUseSelectorHook,
  useDispatch as useReduxDispatch,
  useSelector as useReduxSelector,
} from 'react-redux';

import { IRootState, Action } from 'redux/store';

export const useSelector: TypedUseSelectorHook<IRootState> = useReduxSelector;
export const useDispatch: () => Dispatch = useReduxDispatch;

export function useAction<T extends ActionCreator<Action>>(action: T) {
  const dispatch = useDispatch();

  return useCallback(
    (payload?: Parameters<T>[0]) => {
      dispatch(action(payload));
    },
    [action, dispatch],
  );
}
