import { combineReducers, configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';

import { authArgs } from 'constants/auth';
import Auth from 'pages/Auth';
import Dashboard from 'pages/Dashboard';
import theme from 'redux/slice/theme.slice';
import { store } from 'redux/store';

export default function App() {
  if (authArgs) {
    const authStore = configureStore({
      reducer: combineReducers({ theme }),
    });

    return (
      <Provider store={authStore}>
        <Auth {...authArgs} />
      </Provider>
    );
  } else {
    return (
      <Provider store={store}>
        <Dashboard />
      </Provider>
    );
  }
}
