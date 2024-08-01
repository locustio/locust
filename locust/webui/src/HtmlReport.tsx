import ReactDOM from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';

import FallbackRender from 'components/FallbackRender/FallbackRender';
import { htmlReportProps } from 'constants/swarm';
import HtmlReport from 'pages/HtmlReport';
import { IReport } from 'types/swarm.types';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
  <ErrorBoundary fallbackRender={FallbackRender}>
    <HtmlReport {...(htmlReportProps as IReport)} />
  </ErrorBoundary>,
);
