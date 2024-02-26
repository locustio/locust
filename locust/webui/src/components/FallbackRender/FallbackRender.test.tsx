/* eslint-disable no-console */
import { ErrorBoundary } from 'react-error-boundary';
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';

import App from 'App';
import FallbackRender from 'components/FallbackRender/FallbackRender';
import * as swarmConstants from 'constants/swarm';
import { renderWithProvider } from 'test/testUtils';

describe('Fallback', () => {
  const originalConsoleError = console.error;

  beforeAll(() => {
    /* Suppress console.error
        Because our render function will not return an error,
        Vitest will not suppress the error for us
    */
    console.error = () => {};
  });

  afterAll(() => {
    console.error = originalConsoleError;
  });

  it('renders the FallbackRender when something unexpected happens', () => {
    // break the app
    (vi.mocked(swarmConstants) as any).htmlReportProps = {};

    const { getByText } = renderWithProvider(
      <ErrorBoundary fallbackRender={FallbackRender}>
        <App />
      </ErrorBoundary>,
    );

    expect(getByText('Something went wrong')).toBeTruthy();
  });
});
