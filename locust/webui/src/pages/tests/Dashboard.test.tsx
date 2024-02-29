import { waitFor } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import { SWARM_STATE } from 'constants/swarm';
import Dashboard from 'pages/Dashboard';
import { renderWithProvider } from 'test/testUtils';

describe('Dashboard', () => {
  test('renders the layout', () => {
    const { getByRole } = renderWithProvider(<Dashboard />);

    const logo = getByRole('img');
    const heading = getByRole('link', { name: 'Locust' });

    expect(heading).toBeTruthy();
    expect(heading.getAttribute('href')).toEqual('/');
    expect(logo).toBeTruthy();
    expect(logo.getAttribute('src')).toEqual('./assets/logo.png');
  });

  test('renders the swarm form by default', () => {
    const { getByText } = renderWithProvider(<Dashboard />);

    expect(getByText('Start new load test')).toBeTruthy();
  });

  test('renders the tabs when swarm state is running', async () => {
    const { getByText } = renderWithProvider(<Dashboard />, {
      swarm: { state: SWARM_STATE.RUNNING },
    });

    await waitFor(async () => {
      expect(getByText('Status').nextElementSibling?.textContent).toBe(SWARM_STATE.RUNNING);
    });
  });
});
