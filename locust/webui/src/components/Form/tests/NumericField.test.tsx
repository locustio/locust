import { act } from 'react';
import { fireEvent } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import NumericField from 'components/Form/NumericField';
import { renderWithProvider } from 'test/testUtils';

describe('NumericField', () => {
  test('renders a text field', () => {
    const fieldName = 'numericField';
    const fieldLabel = 'Numeric Field';

    const { getByLabelText } = renderWithProvider(
      <NumericField label={fieldLabel} name={fieldName} />,
    );

    const numericField = getByLabelText(fieldLabel);

    expect(numericField).toBeTruthy();
    expect(numericField.getAttribute('name')).toBe(fieldName);
    expect(numericField.getAttribute('type')).toBe('text');
  });

  test('filters a non-numeric value input', () => {
    const fieldName = 'numericField';
    const fieldLabel = 'Numeric Field';

    const { getByLabelText } = renderWithProvider(
      <NumericField label={fieldLabel} name={fieldName} />,
    );

    const numericField = getByLabelText(fieldLabel);

    act(() => {
      fireEvent.change(numericField, { target: { value: '123hello' } });
    });

    expect(numericField.getAttribute('value')).toBe('123');
  });

  test('allows at most one decimal point', () => {
    const fieldName = 'numericField';
    const fieldLabel = 'Numeric Field';

    const { getByLabelText } = renderWithProvider(
      <NumericField label={fieldLabel} name={fieldName} />,
    );

    const numericField = getByLabelText(fieldLabel);

    act(() => {
      fireEvent.change(numericField, { target: { value: '1.23' } });
      fireEvent.change(numericField, { target: { value: '1.23.' } });
      fireEvent.change(numericField, { target: { value: '1.234' } });
    });

    expect(numericField.getAttribute('value')).toBe('1.234');
  });

  test('allows a decimal point as the first value', () => {
    const fieldName = 'numericField';
    const fieldLabel = 'Numeric Field';

    const { getByLabelText } = renderWithProvider(
      <NumericField label={fieldLabel} name={fieldName} />,
    );

    const numericField = getByLabelText(fieldLabel);

    act(() => {
      fireEvent.change(numericField, { target: { value: '.23' } });
    });

    expect(numericField.getAttribute('value')).toBe('.23');
  });
});
