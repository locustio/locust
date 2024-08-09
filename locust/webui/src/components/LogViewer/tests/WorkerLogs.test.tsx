import { act, fireEvent, render } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import WorkerLogs from '../WorkerLogs';

const workerLogs = ['Worker Log 1', 'ERROR Worker Log 2'];
const workerId = 'worker-1';

describe('WorkerLogs', () => {
  test('should render a notification with important worker logs', () => {
    const { getByTestId } = render(<WorkerLogs logs={workerLogs} workerId={workerId} />);

    expect(getByTestId('worker-notification')).toBeTruthy();
  });

  test('should hide notification and store log index when expanding logs', () => {
    const { queryByTestId, getByTestId, getByRole } = render(
      <WorkerLogs logs={workerLogs} workerId={workerId} />,
    );

    expect(getByTestId('worker-notification')).toBeTruthy();

    const button = getByRole('button', { name: workerId });

    act(() => {
      fireEvent.click(button);
    });

    expect(queryByTestId('worker-notification')).toBeFalsy();
    expect(localStorage[workerId]).toBe(String(workerLogs.length));
  });
});
