import { describe, expect, test } from 'vitest';

import CustomInput from 'components/Form/CustomInput';
import { renderWithProvider } from 'test/testUtils';

describe('SwarmCustomParameters', () => {
  test('renders a text field', () => {
    const fieldName = 'textField';
    const fieldLabel = 'Text Field';
    const fieldDefaultValue = 'value';

    const { getByLabelText } = renderWithProvider(
      <CustomInput defaultValue={fieldDefaultValue} label={fieldLabel} name={fieldName} />,
    );

    const textField = getByLabelText(fieldLabel);

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(fieldName);
    expect(textField.getAttribute('type')).toBe('text');
    expect(textField.getAttribute('value')).toBe(fieldDefaultValue);
  });

  test('renders a password field', () => {
    const fieldName = 'passwordField';
    const fieldLabel = 'Password Field';
    const fieldDefaultValue = 'Secret value';

    const { getByLabelText } = renderWithProvider(
      <CustomInput defaultValue={fieldDefaultValue} isSecret label={fieldLabel} name={fieldName} />,
    );

    const textField = getByLabelText(fieldLabel);

    expect(textField).toBeTruthy();
    expect(textField.getAttribute('name')).toBe(fieldName);
    expect(textField.getAttribute('type')).toBe('password');
    expect(textField.getAttribute('value')).toBe(fieldDefaultValue);
  });

  test('renders a select component when choices are provided', () => {
    const fieldName = 'options';
    const fieldLabel = 'Options';

    const firstCustomChoice = 'Option1';
    const secondCustomChoice = 'Option2';

    const { getByLabelText, getByText } = renderWithProvider(
      <CustomInput
        choices={[firstCustomChoice, secondCustomChoice]}
        defaultValue={firstCustomChoice}
        label={fieldLabel}
        name={fieldName}
      />,
    );

    const selectField = getByLabelText(fieldLabel);
    const option1 = getByText(firstCustomChoice);
    const option2 = getByText(secondCustomChoice);

    expect(selectField).toBeTruthy();

    expect(option1.parentElement instanceof HTMLSelectElement).toBeTruthy();
    expect(option1.parentElement?.getAttribute('name')).toBe(fieldName);

    expect(option1 instanceof HTMLOptionElement).toBeTruthy();
    expect(option2 instanceof HTMLOptionElement).toBeTruthy();

    // Sets default value
    expect(option1.hasAttribute('selected')).toBeTruthy();
    expect(option2.hasAttribute('selected')).toBeFalsy();
  });

  test('renders a checkbox when a boolean default value is provided', () => {
    const fieldTruthyName = 'truthyBoolean';
    const fieldTruthyLabel = 'Truthy Boolean';
    const fieldFalseyName = 'falseyBoolean';
    const fieldFalseyLabel = 'Falsey Boolean';

    const { getByLabelText } = renderWithProvider(
      <>
        <CustomInput defaultValue={true} label={fieldTruthyLabel} name={fieldTruthyName} />
        <CustomInput defaultValue={false} label={fieldFalseyLabel} name={fieldFalseyName} />
      </>,
    );

    const booleanField = getByLabelText(fieldTruthyLabel) as HTMLInputElement;
    const uncheckedBooleanField = getByLabelText(fieldFalseyLabel) as HTMLInputElement;

    expect(booleanField).toBeTruthy();
    expect(booleanField.getAttribute('name')).toBe(fieldTruthyName);
    expect(booleanField.getAttribute('type')).toBe('checkbox');
    expect(booleanField.checked).toBeTruthy();
    expect(uncheckedBooleanField.getAttribute('name')).toBe(fieldFalseyName);
    expect(uncheckedBooleanField.checked).toBeFalsy();
  });

  test('allows defaultValue to be null for text, password, and select fields', () => {
    const customTextField = 'textField';
    const customPasswordField = 'passwordField';
    const customChoicesField = 'customChoices';
    const firstCustomChoice = 'Option1';
    const secondCustomChoice = 'Option2';

    const { getByLabelText } = renderWithProvider(
      <>
        <CustomInput label={customTextField} name={customTextField} />
        <CustomInput isSecret label={customPasswordField} name={customPasswordField} />
        <CustomInput
          choices={[firstCustomChoice, secondCustomChoice]}
          label={customChoicesField}
          name={customChoicesField}
        />
      </>,
    );

    const textField = getByLabelText(customTextField) as HTMLInputElement;
    const passwordField = getByLabelText(customPasswordField) as HTMLInputElement;
    const choicesField = getByLabelText(customChoicesField) as HTMLInputElement;

    expect(textField).toBeTruthy();
    expect(passwordField).toBeTruthy();
    expect(choicesField).toBeTruthy();
    expect(textField.value).toBe('');
    expect(passwordField.value).toBe('');
    expect(choicesField.value).toBe(firstCustomChoice);
  });
});
