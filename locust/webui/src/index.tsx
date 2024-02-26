import ReactDOM from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';

import App from 'App';
import FallbackRender from 'components/FallbackRender/FallbackRender';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
  <ErrorBoundary fallbackRender={FallbackRender}>
    <App />
  </ErrorBoundary>,
);
