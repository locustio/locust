import { afterEach, describe, expect, test } from 'vitest';

import useNotifications from 'hooks/useNotifications';
import { IRootState } from 'redux/store';
import { renderWithProvider } from 'test/testUtils';

function MockHook({
  data,
  notificationKey,
  shouldNotify,
}: {
  data: any[];
  notificationKey: string;
  shouldNotify?: () => boolean;
}) {
  useNotifications(data, { key: notificationKey, shouldNotify });

  return null;
}

describe('useNotifications', () => {
  afterEach(() => {
    localStorage.clear();
  });

  test('should set notifications when there is data', async () => {
    const testArrayKey = 'testArray';

    const { store } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificationKey={testArrayKey} />,
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeTruthy();
  });

  test('should store the current length of data', async () => {
    const temp = localStorage;
    localStorage = {} as typeof localStorage;

    const testArrayKey = 'testArray';

    const mockArray = [1, 2, 3];

    renderWithProvider(<MockHook data={[1, 2, 3]} notificationKey={testArrayKey} />);

    expect(localStorage[`${testArrayKey}Notification`]).toBe(mockArray.length);

    localStorage = temp;
  });

  test('should set notifications when shouldNotify returns true', async () => {
    const testArrayKey = 'testArray';

    const shouldNotify = () => true;

    const { store } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificationKey={testArrayKey} shouldNotify={shouldNotify} />,
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeTruthy();
  });

  test('should not set notifications when data is empty', async () => {
    const testArrayKey = 'testArray';

    const { store } = renderWithProvider(<MockHook data={[]} notificationKey={testArrayKey} />);

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeFalsy();
  });

  test('should not set notifications when viewing page', async () => {
    const testKey = 'testKey';

    const { store } = renderWithProvider(<MockHook data={[]} notificationKey={testKey} />, {
      url: {
        query: {
          tab: testKey,
        },
      },
    });

    expect((store.getState() as IRootState).notification[testKey]).toBeFalsy();
  });

  test('should not set notifications when shouldNotify is false', async () => {
    const testArrayKey = 'testArray';

    const shouldNotify = () => false;

    const { store } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificationKey={testArrayKey} shouldNotify={shouldNotify} />,
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeFalsy();
  });
});
