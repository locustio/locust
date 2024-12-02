import { configureStore } from '@reduxjs/toolkit';

import { api } from 'redux/api/swarm';
import rootReducer, { IRootState } from 'redux/slice/root.slice';

export const store = configureStore({
  reducer: rootReducer,
  middleware: getDefaultMiddleware => getDefaultMiddleware().concat(api.middleware),
});

export const createStore = (preloadedState: Partial<IRootState>) =>
  configureStore({
    reducer: rootReducer,
    middleware: getDefaultMiddleware => getDefaultMiddleware().concat(api.middleware),
    preloadedState,
  });

export type { IRootState, Action } from 'redux/slice/root.slice';
export default configureStore;
