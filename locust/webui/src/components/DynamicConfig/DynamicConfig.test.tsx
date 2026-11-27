import { fireEvent, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterEach, afterAll, describe, expect, test } from 'vitest';

import DynamicConfig from 'components/DynamicConfig/DynamicConfig';
import { TEST_BASE_API } from 'test/constants';
import { renderWithProvider } from 'test/testUtils';

const configMock = {
  ShopUser: { enabled: true, ratio: 1, name: 'shop', nested: { weights: [1, 2] } },
  SearchUser: { rate: 0.5 },
};

let postedBody: unknown;

const server = setupServer(
  http.get(`${TEST_BASE_API}/dynamic-config`, () => HttpResponse.json(configMock)),
  http.post(`${TEST_BASE_API}/dynamic-config`, async ({ request }) => {
    postedBody = await request.json();
    return HttpResponse.json({
      success: true,
      message: 'Dynamic config updated',
      config: postedBody,
    });
  }),
);

describe('DynamicConfig', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    postedBody = undefined;
  });
  afterAll(() => server.close());

  test('renders the settings of every user class', async () => {
    const { findByText, getByLabelText } = renderWithProvider(<DynamicConfig />);

    expect(await findByText('ShopUser')).toBeTruthy();
    expect(await findByText('SearchUser')).toBeTruthy();
    expect(getByLabelText('ratio')).toHaveProperty('value', '1');
    expect(getByLabelText('name')).toHaveProperty('value', 'shop');
    expect(getByLabelText('weights')).toHaveProperty('value', '[1,2]');
    expect(getByLabelText('rate')).toHaveProperty('value', '0.5');
  });

  test('sends the edited settings of all user classes', async () => {
    const { findByLabelText, getByLabelText, getByText, findByText } = renderWithProvider(
      <DynamicConfig />,
    );

    fireEvent.change(await findByLabelText('ratio'), { target: { value: '5' } });
    fireEvent.change(getByLabelText('rate'), { target: { value: '2.5' } });
    fireEvent.change(getByLabelText('weights'), { target: { value: '[3, 4, 5]' } });
    fireEvent.click(getByLabelText('enabled'));
    fireEvent.click(getByText('Update Config'));

    expect(await findByText('Dynamic config updated')).toBeTruthy();
    expect(postedBody).toEqual({
      ShopUser: { enabled: false, ratio: 5, name: 'shop', nested: { weights: [3, 4, 5] } },
      SearchUser: { rate: 2.5 },
    });
  });

  test('does not change the type of a setting while it is being edited', async () => {
    const { findByLabelText, getByText, findByText } = renderWithProvider(<DynamicConfig />);

    const ratio = await findByLabelText('ratio');
    fireEvent.change(ratio, { target: { value: 'abc' } });

    expect(await findByText('Enter a valid JSON number')).toBeTruthy();

    fireEvent.click(getByText('Update Config'));
    await waitFor(() => expect(postedBody).toBeDefined());
    expect((postedBody as typeof configMock).ShopUser.ratio).toBe(1);
  });

  test('shows the error message of a rejected update', async () => {
    server.use(
      http.post(`${TEST_BASE_API}/dynamic-config`, () =>
        HttpResponse.json(
          { success: false, message: "Unknown setting(s) for user class 'ShopUser': x" },
          { status: 400 },
        ),
      ),
    );
    const { findByText, getByText } = renderWithProvider(<DynamicConfig />);

    await findByText('ShopUser');
    fireEvent.click(getByText('Update Config'));

    expect(await findByText("Unknown setting(s) for user class 'ShopUser': x")).toBeTruthy();
  });
});
