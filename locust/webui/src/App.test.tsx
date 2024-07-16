import { describe, expect, it, vi } from 'vitest';

import App from 'App';
import * as authConstants from 'constants/auth';
import { renderWithProvider } from 'test/testUtils';

describe('App', () => {
  it('renders Dashboard by default', () => {
    const { getByText } = renderWithProvider(<App />);

    expect(getByText('Start new load test')).toBeTruthy();
  });

  it('renders Auth component when authArgs is present', () => {
    vi.mocked(authConstants).authArgs = { usernamePasswordCallback: '/auth' };

    const { getByRole, getByLabelText } = renderWithProvider(<App />);

    expect(getByRole('button', { name: 'Login' })).toBeTruthy();
    expect(getByLabelText('Username')).toBeTruthy();
    expect(getByLabelText('Password')).toBeTruthy();

    (vi.mocked(authConstants) as any).authArgs = undefined;
  });
});
