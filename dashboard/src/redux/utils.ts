import { Action } from 'redux/store';
import { merge } from 'utils/object';

export function updateStateWithPayload<ReducerState, ActionType extends Action = Action>(
  state: ReducerState,
  { payload }: ActionType,
) {
  return merge(state, payload);
}
