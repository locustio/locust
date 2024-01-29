import { act, fireEvent } from '@testing-library/react';
import { http } from 'msw';
import { setupServer } from 'msw/node';
import { afterEach, afterAll, beforeAll, describe, test, expect, vi } from 'vitest';

import SwarmUserClassPicker from 'components/SwarmForm/SwarmUserClassPicker';
import { TEST_BASE_API } from 'test/constants';
import { renderWithProvider } from 'test/testUtils';
import { camelCaseKeys } from 'utils/string';

const updateSelectedClasses = vi.fn();
const updateSwarm = vi.fn();
const updateUserSettings = vi.fn();

const server = setupServer(
  http.post(`${TEST_BASE_API}/user`, async ({ request }) =>
    updateUserSettings(camelCaseKeys((await request.json()) as Record<string, any>)),
  ),
);

const mockUsers = {
  Example: {
    host: 'http://localhost',
    fixedCount: 0,
    weight: 0,
    tasks: ['ExampleTask', 'SecondTask'],
  },
  ExampleTwo: {
    host: 'http://localhost:2',
    fixedCount: 0,
    weight: 0,
    tasks: ['ExampleTaskTwo'],
  },
};

const availableUserTasks = Object.entries(mockUsers).reduce(
  (tasks, [key, value]) => ({
    ...tasks,
    [key]: value.tasks,
  }),
  {},
);

const defaultProps = {
  selectedUserClasses: Object.keys(mockUsers),
  setSelectedUserClasses: updateSelectedClasses,
  setSwarm: updateSwarm,
};

describe('SwarmUserClassPicker', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    updateSelectedClasses.mockClear();
    updateSwarm.mockClear();
    updateUserSettings.mockClear();
  });
  afterAll(() => server.close());

  test('should render the users', () => {
    const { getByText } = renderWithProvider(<SwarmUserClassPicker {...defaultProps} />, {
      swarm: {
        users: mockUsers,
      },
    });

    Object.entries(mockUsers).forEach(([key, value]) => {
      expect(getByText(key)).to.be.ok;
      expect(getByText(value.host)).to.be.ok;
    });
  });

  test('should update the selected users on click', () => {
    const { getAllByRole } = renderWithProvider(<SwarmUserClassPicker {...defaultProps} />, {
      swarm: {
        users: mockUsers,
      },
    });

    act(() => {
      fireEvent.click(getAllByRole('checkbox')[0]);
    });

    expect(updateSelectedClasses.mock.calls[0][0]).toEqual([Object.keys(mockUsers)[1]]);
  });

  test('should allow for configuring the user', async () => {
    const { getByRole, getAllByRole } = renderWithProvider(
      <SwarmUserClassPicker {...defaultProps} />,
      {
        swarm: {
          availableUserTasks,
          users: mockUsers,
        },
      },
    );

    vi.useFakeTimers();

    act(() => {
      // Open modal
      fireEvent.click(getAllByRole('button')[0]);
    });
    act(() => {
      // Save settings
      fireEvent.click(getByRole('button', { name: 'Save' }));
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(updateUserSettings).toHaveBeenCalled();

    const submittedData = updateUserSettings.mock.calls[0][0];

    expect(submittedData).toEqual({ ...mockUsers.Example, userClassName: 'Example' });
  });

  test('should allow for configuring tasks, host, fixed_count, and weight to be modified', async () => {
    const updatedUser = {
      weight: 30,
      host: 'http://localhost.new',
      fixedCount: 10,
      tasks: ['SecondTask'],
    };

    const { store, getByRole, getAllByRole, getByLabelText } = renderWithProvider(
      <SwarmUserClassPicker {...defaultProps} />,
      {
        swarm: {
          availableUserTasks,
          users: mockUsers,
        },
      },
    );

    vi.useFakeTimers();

    act(() => {
      // Open modal
      fireEvent.click(getAllByRole('button')[0]);
    });
    act(() => {
      // Update settings
      fireEvent.change(getByLabelText('Tasks'), {
        target: { value: updatedUser.tasks[0] },
      });
      fireEvent.change(getByLabelText('Host'), {
        target: { value: updatedUser.host },
      });
      fireEvent.change(getByLabelText('Fixed Count'), {
        target: { value: String(updatedUser.fixedCount) },
      });
      fireEvent.change(getByLabelText('Weight'), {
        target: { value: String(updatedUser.weight) },
      });
      // Save settings
      fireEvent.click(getByRole('button', { name: 'Save' }));
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(updateUserSettings).toHaveBeenCalled();

    const submittedData = updateUserSettings.mock.calls[0][0];

    expect(submittedData).toEqual({ ...updatedUser, userClassName: 'Example' });
    expect(store.getState().swarm.users.Example).toEqual(updatedUser);
  });
});
