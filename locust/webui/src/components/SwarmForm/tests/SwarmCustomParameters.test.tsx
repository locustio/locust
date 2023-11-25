import { describe, expect, test } from 'vitest';

import SwarmCustomParameters from 'components/SwarmForm/SwarmCustomParameters';
import { renderWithProvider } from 'test/testUtils';
import { toTitleCase } from 'utils/string';

describe('SwarmCustomParameters', () => {
  test('renders accordion with correct label', () => {
    const { getByText } = renderWithProvider(<SwarmCustomParameters extraOptions={{}} />);

    expect(getByText('Custom parameters')).toBeTruthy();
  });

  test('renders a text field', () => {
    const customFieldName = 'textField';
    const customFieldValue = 'Text value';

    const { getByLabelText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: null,
            isSecret: false,
          },
        }}
      />,
    );

    const textField = getByLabelText(toTitleCase(customFieldName));

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(customFieldName);
    expect(textField.getAttribute('type')).toBe('text');
    expect(textField.getAttribute('value')).toBe(customFieldValue);
  });

  test('renders a text field with help text', () => {
    const customFieldName = 'textField';
    const customFieldValue = 'Text value';
    const customFieldHelpText = 'Help Text';

    const { getByLabelText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: customFieldHelpText,
            isSecret: false,
          },
        }}
      />,
    );

    const textField = getByLabelText(`${toTitleCase(customFieldName)} (${customFieldHelpText})`);

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(customFieldName);
    expect(textField.getAttribute('type')).toBe('text');
    expect(textField.getAttribute('value')).toBe(customFieldValue);
  });

  test('renders a password field', () => {
    const customFieldName = 'passwordField';
    const customFieldValue = 'Secret value';

    const { getByLabelText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: null,
            isSecret: true,
          },
        }}
      />,
    );

    const textField = getByLabelText(toTitleCase(customFieldName));

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(customFieldName);
    expect(textField.getAttribute('type')).toBe('password');
    expect(textField.getAttribute('value')).toBe(customFieldValue);
  });

  test('renders a password field with help text', () => {
    const customFieldName = 'passwordField';
    const customFieldValue = 'Secret value';
    const customFieldHelpText = 'Secret Help Text';

    const { getByLabelText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: customFieldHelpText,
            isSecret: true,
          },
        }}
      />,
    );

    const textField = getByLabelText(`${toTitleCase(customFieldName)} (${customFieldHelpText})`);

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(customFieldName);
    expect(textField.getAttribute('type')).toBe('password');
    expect(textField.getAttribute('value')).toBe(customFieldValue);
  });

  test('renders a select component when choices are provided', () => {
    const customFieldName = 'extraOptions';
    const firstCustomChoice = 'Option1';
    const secondCustomChoice = 'Option2';

    const { getByLabelText, getByText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: [firstCustomChoice, secondCustomChoice],
            defaultValue: firstCustomChoice,
            helpText: null,
            isSecret: false,
          },
        }}
      />,
    );

    const selectField = getByLabelText(toTitleCase(customFieldName));
    const option1 = getByText(firstCustomChoice);
    const option2 = getByText(secondCustomChoice);

    expect(selectField).toBeTruthy();

    expect(option1.parentElement instanceof HTMLSelectElement).toBeTruthy();
    expect(option1.parentElement?.getAttribute('name')).toBe(customFieldName);

    expect(option1 instanceof HTMLOptionElement).toBeTruthy();
    expect(option2 instanceof HTMLOptionElement).toBeTruthy();

    // Sets default value
    expect(option1.hasAttribute('selected')).toBeTruthy();
    expect(option2.hasAttribute('selected')).toBeFalsy();
  });

  test('renders a select component with help text when choices and help text are provided', () => {
    const customFieldName = 'extraOptions';
    const customFieldHelpText = 'Help Text';

    const { getByLabelText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldName]: {
            choices: ['Option1', 'Option2'],
            defaultValue: 'Option1',
            helpText: customFieldHelpText,
            isSecret: false,
          },
        }}
      />,
    );

    const selectField = getByLabelText(`${toTitleCase(customFieldName)} (${customFieldHelpText})`);

    expect(selectField).toBeTruthy();
  });

  test('renders null or boolean parameters as invalid', () => {
    const customFieldNullDefaultValue = 'nullDefaultValue';
    const customFieldBooleanDefaultValue = 'booleanDefaultValue';

    const { getByText } = renderWithProvider(
      <SwarmCustomParameters
        extraOptions={{
          [customFieldNullDefaultValue]: {
            choices: null,
            defaultValue: null,
            helpText: null,
            isSecret: false,
          },
          [customFieldBooleanDefaultValue]: {
            choices: null,
            defaultValue: true,
            helpText: null,
            isSecret: false,
          },
        }}
      />,
    );

    const invalidParametersHeader = getByText(
      "The following custom parameters can't be set in the Web UI, because it is a boolean or None type:",
    );
    const invalidParametersList = invalidParametersHeader.nextSibling;

    expect(invalidParametersHeader).toBeTruthy();
    expect(invalidParametersList instanceof HTMLUListElement).toBeTruthy();
    expect(invalidParametersList?.textContent).toContain(customFieldNullDefaultValue);
    expect(invalidParametersList?.textContent).toContain(customFieldBooleanDefaultValue);
  });
});
