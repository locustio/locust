import { PayloadAction } from '@reduxjs/toolkit';

import { shallowMerge } from 'utils/object';

export function updateStateWithPayload<
  ReducerState,
  ActionType extends PayloadAction<any> = PayloadAction<any>,
>(state: ReducerState, { payload }: ActionType) {
  return shallowMerge(state, payload);
}
