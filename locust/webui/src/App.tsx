import { combineReducers, configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';

import { authArgs } from 'constants/auth';
import { htmlReportProps } from 'constants/swarm';
import Auth from 'pages/Auth';
import Dashboard from 'pages/Dashboard';
import HtmlReport from 'pages/HtmlReport';
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
  } else if (htmlReportProps) {
    return <HtmlReport {...htmlReportProps} />;
  } else {
    return (
      <Provider store={store}>
        <Dashboard />
      </Provider>
    );
  }
}
