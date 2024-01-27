import { render } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import Select from 'components/Form/Select';

const selectedOptionsToArray = (selectElement: HTMLSelectElement) =>
  Array.from(selectElement.selectedOptions).map(option => option.value);

describe('Select component', () => {
  test('should set defaultValue as first option', () => {
    const options = ['Option 1', 'Option 2', 'Option 3'];

    const { getByLabelText } = render(
      <Select label='Select Input' name='selectInput' options={options} />,
    );

    expect((getByLabelText('Select Input') as HTMLSelectElement).value).toBe(options[0]);
  });

  test('should set defaultValue as all provided option in multi-select', () => {
    const options = ['Option 1', 'Option 2', 'Option 3'];

    const { getByLabelText } = render(
      <Select label='Select Input' multiple name='selectInput' options={options} />,
    );

    expect(selectedOptionsToArray(getByLabelText('Select Input') as HTMLSelectElement)).toEqual(
      options,
    );
  });

  test('should allow defaultValue to be set', async () => {
    const options = ['Option 1', 'Option 2', 'Option 3'];

    const { getByLabelText } = render(
      <Select
        defaultValue={options[1]}
        label='Select Input'
        name='selectInput'
        options={options}
      />,
    );

    expect((getByLabelText('Select Input') as HTMLSelectElement).value).toBe(options[1]);
  });

  test('should allow defaultValue to be set in multi-select', async () => {
    const options = ['Option 1', 'Option 2', 'Option 3'];

    const { getByLabelText } = render(
      <Select
        defaultValue={options[1]}
        label='Select Input'
        name='selectInput'
        options={options}
      />,
    );

    expect(selectedOptionsToArray(getByLabelText('Select Input') as HTMLSelectElement)).toEqual([
      options[1],
    ]);
  });
});
