import { describe, expect, test } from 'vitest';

import Auth from 'pages/Auth';
import { renderWithProvider } from 'test/testUtils';

describe('Auth', () => {
  test('renders login form when usernamePasswordCallback is provided', () => {
    const mockAuthArgs = {
      usernamePasswordCallback: '/auth',
    };

    const { getByLabelText, getByRole } = renderWithProvider(<Auth {...mockAuthArgs} />);

    expect(getByLabelText('Username')).toBeTruthy();
    expect(getByLabelText('Password')).toBeTruthy();
    expect(getByRole('button', { name: 'Login' })).toBeTruthy();
  });

  test('does not render the login form when usernamePasswordCallback is not provided', () => {
    const { queryByRole, queryByLabelText } = renderWithProvider(<Auth />);

    expect(queryByLabelText('Username')).toBeNull();
    expect(queryByLabelText('Password')).toBeNull();
    expect(queryByRole('button', { name: 'Login' })).toBeNull();
  });

  test('renders error alert when an error is provided', () => {
    const mockAuthArgs = {
      usernamePasswordCallback: '/auth',
      error: 'Invalid credentials',
    };

    const { getByText } = renderWithProvider(<Auth {...mockAuthArgs} />);

    expect(getByText('Invalid credentials')).toBeTruthy();
  });

  test('renders auth providers when authProviders are provided', () => {
    const googleProvider = {
      label: 'Google',
      callbackUrl: '/google-auth',
      iconUrl: '/google-icon.png',
    };
    const githubProvider = {
      label: 'Github',
      callbackUrl: '/github-auth',
      iconUrl: '/github-icon.png',
    };

    const mockAuthArgs = {
      authProviders: [googleProvider, githubProvider],
    };

    const { getAllByRole, getByRole } = renderWithProvider(<Auth {...mockAuthArgs} />);

    const googleLink = getByRole('link', { name: googleProvider.label });
    const githubLink = getByRole('link', { name: githubProvider.label });
    const icons = getAllByRole('img');

    expect(googleLink).toBeTruthy();
    expect(googleLink.getAttribute('href')).toEqual(googleProvider.callbackUrl);
    expect(icons[1].getAttribute('src')).toEqual(googleProvider.iconUrl);

    expect(githubLink).toBeTruthy();
    expect(githubLink.getAttribute('href')).toEqual(githubProvider.callbackUrl);
    expect(icons[2].getAttribute('src')).toEqual(githubProvider.iconUrl);
  });
});
