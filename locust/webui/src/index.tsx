import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import App from 'App';
import { swarmTemplateArgs } from 'constants/swarm';
import { store } from 'redux/store';
import Report from 'Report';
import { IReportTemplateArgs } from 'types/swarm.types';
import { ICharts } from 'types/ui.types';
import { updateArraysAtProps } from 'utils/object';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

if ((swarmTemplateArgs as IReportTemplateArgs).isReport) {
  const reportProps = {
    ...(swarmTemplateArgs as IReportTemplateArgs),
    charts: swarmTemplateArgs.history.reduce(
      (charts, { currentResponseTimePercentiles, ...history }) =>
        updateArraysAtProps(charts, { ...currentResponseTimePercentiles, ...history }),
      {} as ICharts,
    ) as ICharts,
  };
  root.render(<Report {...reportProps} />);
} else {
  root.render(
    <Provider store={store}>
      <App />
    </Provider>,
  );
}
