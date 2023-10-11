import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import App from 'App';
import { store } from 'redux/store';
import Report from 'Report';
import { IReportTemplateArgs } from 'types/swarm.types';
import { ICharts } from 'types/ui.types';
import { updateArraysAtProps } from 'utils/object';
import { camelCaseKeys } from 'utils/string';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

if ((window.templateArgs as IReportTemplateArgs).is_report) {
  const templateArgs = camelCaseKeys(window.templateArgs) as IReportTemplateArgs;
  const reportProps = {
    ...templateArgs,
    charts: templateArgs.history.reduce(updateArraysAtProps, {}) as ICharts,
  };
  root.render(<Report {...reportProps} />);
} else {
  root.render(
    <Provider store={store}>
      <App />
    </Provider>,
  );
}
