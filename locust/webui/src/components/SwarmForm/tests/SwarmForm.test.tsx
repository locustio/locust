import { act, fireEvent, waitFor } from '@testing-library/react';
import { http } from 'msw';
import { setupServer } from 'msw/node';
import { afterEach, afterAll, beforeAll, describe, test, expect, vi } from 'vitest';

import SwarmForm from 'components/SwarmForm/SwarmForm';
import { TEST_BASE_API } from 'test/constants';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';
import { camelCaseKeys, queryStringToObject, toTitleCase } from 'utils/string';

const startSwarm = vi.fn();

const server = setupServer(
  http.post(`${TEST_BASE_API}/swarm`, async ({ request }) =>
    startSwarm(camelCaseKeys(queryStringToObject(await request.text()))),
  ),
);

describe('SwarmForm', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    startSwarm.mockClear();
  });
  afterAll(() => server.close());

  test('should submit form data with default values on button click', async () => {
    const { getByText } = renderWithProvider(<SwarmForm />);

    act(() => {
      fireEvent.click(getByText('Start Swarm'));
    });

    await waitFor(async () => {
      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          host: swarmStateMock.host,
          runTime: '',
          spawnRate: '1',
          userCount: '1',
        });
      }
    });
  });

  test('should edit all inputs in the form', async () => {
    const { getByText, getByLabelText } = renderWithProvider(<SwarmForm />, {
      swarm: {
        showUserclassPicker: true,
        availableUserClasses: ['Class1'],
        availableShapeClasses: ['Shape1', 'Shape2'],
        extraOptions: {},
        users: {},
      },
    });

    act(() => {
      fireEvent.change(getByLabelText('Shape Class'), {
        target: { value: 'Shape1' },
      });
      fireEvent.change(getByLabelText('Number of users (peak concurrency)'), {
        target: { value: '15' },
      });
      fireEvent.change(getByLabelText('Ramp Up (users started/second)'), {
        target: { value: '20' },
      });
      fireEvent.change(getByLabelText('Run time (e.g. 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.)'), {
        target: { value: '2h' },
      });
      fireEvent.change(getByLabelText('Host'), {
        target: { value: 'https://localhost:5000' },
      });

      fireEvent.click(getByText('Start Swarm'));
    });

    await waitFor(async () => {
      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          host: 'https://localhost:5000',
          runTime: '2h',
          spawnRate: '20',
          userCount: '15',
          shapeClass: 'Shape1',
          userClasses: 'Class1',
        });
      }
    });
  });

  test('should allow selected user classes to be modified', async () => {
    const { getByText, getAllByRole } = renderWithProvider(<SwarmForm />, {
      swarm: {
        showUserclassPicker: true,
        availableUserClasses: ['Class1', 'Class2'],
        availableShapeClasses: ['Shape1', 'Shape2'],
        extraOptions: {},
        users: {
          Class1: {
            host: 'http://localhost',
            fixedCount: 0,
            weight: 0,
            tasks: ['ExampleTask'],
          },
          Class2: {
            host: 'http://localhost',
            fixedCount: 0,
            weight: 0,
            tasks: ['ExampleTask'],
          },
        },
      },
    });

    act(() => {
      fireEvent.click(getAllByRole('checkbox')[1]);
    });
    act(() => {
      fireEvent.click(getByText('Start Swarm'));
    });

    await waitFor(async () => {
      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          host: '',
          runTime: '',
          spawnRate: '1',
          userCount: '1',
          shapeClass: 'Shape1',
          userClasses: 'Class1',
        });
      }
    });
  });

  test('should submit provided extraOptions with default values', async () => {
    const customFieldName = 'textField';
    const customFieldValue = 'Text value';
    const customChoiceFieldName = 'choicesField';
    const firstCustomChoice = 'Option1';
    const secondCustomChoice = 'Option2';

    const { getByText } = renderWithProvider(<SwarmForm />, {
      swarm: {
        ...swarmStateMock,
        extraOptions: {
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: null,
            isSecret: false,
          },
          [customChoiceFieldName]: {
            choices: [firstCustomChoice, secondCustomChoice],
            defaultValue: firstCustomChoice,
            helpText: null,
            isSecret: false,
          },
        },
      },
    });

    act(() => {
      fireEvent.click(getByText('Start Swarm'));
    });

    await waitFor(() => {
      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          host: swarmStateMock.host,
          runTime: '',
          spawnRate: '1',
          userCount: '1',
          textField: 'Text value',
          choicesField: 'Option1',
        });
      }
    });
  });

  test('should submit provided extraOptions with changed values', async () => {
    const customFieldName = 'textField';
    const customFieldValue = 'Text value';
    const customChoiceFieldName = 'choicesField';
    const firstCustomChoice = 'Option1';
    const secondCustomChoice = 'Option2';

    const { getByText, getByLabelText } = renderWithProvider(<SwarmForm />, {
      swarm: {
        ...swarmStateMock,
        extraOptions: {
          [customFieldName]: {
            choices: null,
            defaultValue: customFieldValue,
            helpText: null,
            isSecret: false,
          },
          [customChoiceFieldName]: {
            choices: [firstCustomChoice, secondCustomChoice],
            defaultValue: firstCustomChoice,
            helpText: null,
            isSecret: false,
          },
        },
      },
    });

    const textField = getByLabelText(toTitleCase(customFieldName));
    const selectField = getByLabelText(toTitleCase(customChoiceFieldName));

    act(() => {
      fireEvent.change(textField, {
        target: { value: 'Changed text value' },
      });
      fireEvent.change(selectField, {
        target: { value: 'Option2' },
      });

      fireEvent.click(getByText('Start Swarm'));
    });

    await waitFor(async () => {
      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          host: swarmStateMock.host,
          runTime: '',
          spawnRate: '1',
          userCount: '1',
          textField: 'Changed text value',
          choicesField: 'Option2',
        });
      }
    });
  });
});
