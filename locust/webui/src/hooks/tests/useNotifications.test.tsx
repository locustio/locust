import { afterEach, describe, expect, test } from 'vitest';

import useNotifications from 'hooks/useNotifications';
import { IRootState } from 'redux/store';
import { renderWithProvider } from 'test/testUtils';
import { objectLength } from 'utils/object';

function MockHook({
  data,
  notificaitonKey,
  shouldNotify,
}: {
  data: any[] | Record<string, any>;
  notificaitonKey: string;
  shouldNotify?: () => boolean;
}) {
  useNotifications(data, { key: notificaitonKey, shouldNotify });

  return null;
}

describe('useNotifications', () => {
  afterEach(() => {
    localStorage.clear();
  });

  test('should set notifications when there is data', async () => {
    const testArrayKey = 'testArray';
    const testObjectKey = 'testObject';

    const { store: firstRender } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificaitonKey={testArrayKey} />,
    );
    const { store } = renderWithProvider(
      <MockHook data={{ key1: 1, key2: 2 }} notificaitonKey={testObjectKey} />,
      firstRender.getState(),
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeTruthy();
    expect((store.getState() as IRootState).notification[testObjectKey]).toBeTruthy();
  });

  test('should store the current length of data', async () => {
    const temp = localStorage;
    localStorage = {} as typeof localStorage;

    const testArrayKey = 'testArray';
    const testObjectKey = 'testObject';

    const mockArray = [1, 2, 3];
    const mockObject = { key1: 1, key2: 2 };

    renderWithProvider(<MockHook data={[1, 2, 3]} notificaitonKey={testArrayKey} />);
    renderWithProvider(<MockHook data={{ key1: 1, key2: 2 }} notificaitonKey={testObjectKey} />);

    expect(localStorage[`${testArrayKey}Notification`]).toBe(objectLength(mockArray));
    expect(localStorage[`${testObjectKey}Notification`]).toBe(objectLength(mockObject));

    localStorage = temp;
  });

  test('should set notifications when shouldNotify returns true', async () => {
    const testArrayKey = 'testArray';
    const testObjectKey = 'testObject';

    const shouldNotify = () => true;

    const { store: firstRender } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificaitonKey={testArrayKey} shouldNotify={shouldNotify} />,
    );
    const { store } = renderWithProvider(
      <MockHook
        data={{ key1: 1, key2: 2 }}
        notificaitonKey={testObjectKey}
        shouldNotify={shouldNotify}
      />,
      firstRender.getState(),
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeTruthy();
    expect((store.getState() as IRootState).notification[testObjectKey]).toBeTruthy();
  });

  test('should not set notifications when data is empty', async () => {
    const testArrayKey = 'testArray';
    const testObjectKey = 'testObject';

    const { store: firstRender } = renderWithProvider(
      <MockHook data={[]} notificaitonKey={testArrayKey} />,
    );
    const { store } = renderWithProvider(
      <MockHook data={{}} notificaitonKey={testObjectKey} />,
      firstRender.getState(),
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeFalsy();
    expect((store.getState() as IRootState).notification[testObjectKey]).toBeFalsy();
  });

  test('should not set notifications when viewing page', async () => {
    const testKey = 'testKey';

    const { store } = renderWithProvider(<MockHook data={[]} notificaitonKey={testKey} />, {
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
    const testObjectKey = 'testObject';

    const shouldNotify = () => false;

    const { store: firstRender } = renderWithProvider(
      <MockHook data={[1, 2, 3]} notificaitonKey={testArrayKey} shouldNotify={shouldNotify} />,
    );
    const { store } = renderWithProvider(
      <MockHook
        data={{ key1: 1, key2: 2 }}
        notificaitonKey={testObjectKey}
        shouldNotify={shouldNotify}
      />,
      firstRender.getState(),
    );

    expect((store.getState() as IRootState).notification[testArrayKey]).toBeFalsy();
    expect((store.getState() as IRootState).notification[testObjectKey]).toBeFalsy();
  });
});
