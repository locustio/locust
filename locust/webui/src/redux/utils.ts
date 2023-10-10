import { Action } from 'redux/store';
import { shallowMerge } from 'utils/object';

export function updateStateWithPayload<ReducerState, ActionType extends Action = Action>(
  state: ReducerState,
  { payload }: ActionType,
) {
  return shallowMerge(state, payload);
}
