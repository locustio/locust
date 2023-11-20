import { configureStore } from '@reduxjs/toolkit';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';

import { api } from 'redux/api/swarm';
import rootReducer from 'redux/slice/root.slice';

const createStore = (initialState = {}) =>
  configureStore({
    reducer: rootReducer,
    preloadedState: initialState,
    middleware: getDefaultMiddleware => getDefaultMiddleware().concat(api.middleware),
  });

export const renderWithProvider = (Component: React.ReactElement, initialState = {}) => {
  const store = createStore(initialState);

  const renderResult = render(<Provider store={store}>{Component}</Provider>);

  return {
    ...renderResult,
    store,
  };
};

export const rerenderWithProvider = (
  rerender: (ui: React.ReactElement) => void,
  Component: React.ReactElement,
  initialState = {},
) => {
  const store = createStore(initialState);

  rerender(<Provider store={store}>{Component}</Provider>);
};
