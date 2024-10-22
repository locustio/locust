import { act } from 'react';
import { fireEvent } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import PasswordField from 'components/Form/PasswordField';
import { renderWithProvider } from 'test/testUtils';

describe('SwarmCustomParameters', () => {
  test('renders a password field', () => {
    const fieldName = 'passwordField';
    const fieldLabel = 'Password Field';

    const { getByLabelText } = renderWithProvider(
      <PasswordField label={fieldLabel} name={fieldName} />,
    );

    const passwordField = getByLabelText(fieldLabel);

    expect(passwordField).toBeTruthy();
    expect(passwordField.getAttribute('name')).toBe(fieldName);
    expect(passwordField.getAttribute('type')).toBe('password');
  });

  test('displays the password on visibility toggle click', () => {
    const fieldName = 'passwordField';
    const fieldLabel = 'Password Field';

    const { getByRole, getByLabelText } = renderWithProvider(
      <PasswordField label={fieldLabel} name={fieldName} />,
    );

    const visibilityToggle = getByRole('button');
    const passwordField = getByLabelText(fieldLabel);

    act(() => {
      fireEvent.click(visibilityToggle);
    });

    expect(passwordField.getAttribute('type')).toBe('text');
  });
});
