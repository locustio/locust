import LocustWebui from 'LocustWebui';
import { describe, expect, it, vi } from 'vitest';

import * as authConstants from 'constants/auth';
import * as swarmConstants from 'constants/swarm';
import { swarmReportMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

describe('LocustWebui', () => {
  it('renders Dashboard by default', () => {
    const { getByText } = renderWithProvider(<LocustWebui />);

    expect(getByText('Start new load test')).toBeTruthy();
  });

  it('renders Auth component when authArgs is present', () => {
    vi.mocked(authConstants).authArgs = { usernamePasswordCallback: '/auth' };

    const { getByRole, getByLabelText } = renderWithProvider(<LocustWebui />);

    expect(getByRole('button', { name: 'Login' })).toBeTruthy();
    expect(getByLabelText('Username')).toBeTruthy();
    expect(getByLabelText('Password')).toBeTruthy();

    (vi.mocked(authConstants) as any).authArgs = undefined;
  });

  it('renders the HTML Report when isReport is true', () => {
    vi.mocked(swarmConstants).htmlReportProps = swarmReportMock;

    const { getByText } = renderWithProvider(<LocustWebui />);

    expect(getByText('Locust Test Report')).toBeTruthy();
  });
});
