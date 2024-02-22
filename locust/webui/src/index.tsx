import { combineReducers, configureStore } from '@reduxjs/toolkit';
import Auth from 'auth';
import ReactDOM from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';
import { Provider } from 'react-redux';

import App from 'App';
import FallbackRender from 'components/FallbackRender/FallbackRender';
import { swarmTemplateArgs } from 'constants/swarm';
import theme from 'redux/slice/theme.slice';
import { store } from 'redux/store';
import Report from 'Report';
import { IReportTemplateArgs } from 'types/swarm.types';
import { ICharts } from 'types/ui.types';
import { updateArraysAtProps } from 'utils/object';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

function componentToRender() {
  if (window.authArgs) {
    const authStore = configureStore({
      reducer: combineReducers({ theme }),
    });

    return (
      <Provider store={authStore}>
        <Auth />
      </Provider>
    );
  } else if ((swarmTemplateArgs as IReportTemplateArgs).isReport) {
    const reportProps = {
      ...(swarmTemplateArgs as IReportTemplateArgs),
      charts: swarmTemplateArgs.history?.reduce(
        (charts, { currentResponseTimePercentiles, ...history }) =>
          updateArraysAtProps(charts, { ...currentResponseTimePercentiles, ...history }),
        {} as ICharts,
      ) as ICharts,
    };
    return <Report {...reportProps} />;
  } else {
    return (
      <Provider store={store}>
        <App />
      </Provider>
    );
  }
}

root.render(<ErrorBoundary fallbackRender={FallbackRender}>{componentToRender()}</ErrorBoundary>);
