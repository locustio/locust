import { render, fireEvent, act, RenderResult } from '@testing-library/react';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import Form from 'components/Form/Form';

describe('Form component', () => {
  const onSubmitMock = vi.fn();
  let component: RenderResult;

  beforeEach(() => {
    component = render(
      <Form onSubmit={onSubmitMock}>
        <input data-testid='textInput' defaultValue='Text' name='textInput' type='text' />
        <input
          data-testid='numberInput'
          data-type='number'
          defaultValue='4'
          name='numberInput'
          type='text'
        />
        <textarea data-testid='textArea' defaultValue='Text Area' name='textArea' />
        <input
          data-testid='checkboxInput'
          defaultChecked={true}
          name='checkboxInput'
          type='checkbox'
        />
        <select data-testid='selectInput' defaultValue='option1' name='selectInput'>
          <option value='option1'>Option 1</option>
          <option value='option2'>Option 2</option>
          <option value='option3'>Option 3</option>
        </select>
        <select
          data-testid='multipleSelectInput'
          defaultValue={['option2', 'option2']}
          multiple
          name='multipleSelectInput'
        >
          <option value='option1'>Option 1</option>
          <option value='option2'>Option 2</option>
          <option value='option3'>Option 3</option>
        </select>
        <button data-testid='submitButton' type='submit'>
          Submit
        </button>
      </Form>,
    );
  });

  test('should handle all input types with defaultValues', async () => {
    const { getByTestId } = component;

    act(() => {
      fireEvent.click(getByTestId('submitButton'));
    });

    expect(onSubmitMock).toHaveBeenCalledWith({
      textInput: 'Text',
      numberInput: 4,
      textArea: 'Text Area',
      checkboxInput: true,
      selectInput: 'option1',
      multipleSelectInput: ['option2'],
    });
  });

  test('should handle all input types with changed values', async () => {
    const { getByTestId } = component;

    act(() => {
      fireEvent.change(getByTestId('textInput'), {
        target: { value: 'Changed Text' },
      });
      fireEvent.change(getByTestId('numberInput'), {
        target: { value: '6' },
      });
      fireEvent.change(getByTestId('textArea'), {
        target: { value: 'Changed Text Area' },
      });
      fireEvent.click(getByTestId('checkboxInput'));
      fireEvent.change(getByTestId('selectInput'), {
        target: { value: 'option2' },
      });
      fireEvent.change(getByTestId('multipleSelectInput'), { target: { value: 'option3' } });

      fireEvent.click(getByTestId('submitButton'));
    });

    expect(onSubmitMock).toHaveBeenCalledWith({
      textInput: 'Changed Text',
      numberInput: 6,
      textArea: 'Changed Text Area',
      checkboxInput: false,
      selectInput: 'option2',
      multipleSelectInput: ['option3'],
    });
  });
});
