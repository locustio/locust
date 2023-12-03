import { act, fireEvent, waitFor } from '@testing-library/react';
import { http } from 'msw';
import { setupServer } from 'msw/node';
import { afterEach, afterAll, beforeAll, describe, test, expect, vi } from 'vitest';

import SwarmEditForm from 'components/SwarmForm/SwarmEditForm';
import { TEST_BASE_API } from 'test/constants';
import { renderWithProvider } from 'test/testUtils';
import { camelCaseKeys, queryStringToObject } from 'utils/string';

const startSwarm = vi.fn();

const server = setupServer(
  http.post(`${TEST_BASE_API}/swarm`, async ({ request }) =>
    startSwarm(camelCaseKeys(queryStringToObject(await request.text()))),
  ),
);

describe('SwarmEditForm', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  test('should submit form data on button click', async () => {
    const onSubmit = vi.fn();
    const { getByText, getByLabelText } = renderWithProvider(<SwarmEditForm onSubmit={onSubmit} />);

    act(() => {
      fireEvent.change(getByLabelText('Number of users (peak concurrency)'), {
        target: { value: '5' },
      });
      fireEvent.change(getByLabelText('Ramp Up (users started/second)'), {
        target: { value: '10' },
      });

      fireEvent.click(getByText('Update Swarm'));
    });

    await waitFor(async () => {
      expect(onSubmit).toHaveBeenCalled();

      const submittedData = startSwarm.mock.calls[0][0];

      if (submittedData) {
        expect(submittedData).toEqual({
          spawnRate: '10',
          userCount: '5',
        });
      }
    });
  });
});
