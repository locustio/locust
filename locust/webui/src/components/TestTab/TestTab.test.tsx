import { fireEvent } from '@testing-library/react';
import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest';

import TestTab from 'components/TestTab/TestTab';
import { SWARM_STATE } from 'constants/swarm';
import { uiActions } from 'redux/slice/ui.slice';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import { renderWithProvider } from 'test/testUtils';

describe('TestTab', () => {
    beforeEach(() => {
        vi.spyOn(globalThis, 'fetch').mockResolvedValue(
            new Response(JSON.stringify({ status: 'running' }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            }),
        );
    });
    afterEach(() => {
        vi.restoreAllMocks();
    });

    test('renders request form inputs', () => {
        const { getByLabelText, getByText, getByRole } = renderWithProvider(<TestTab />);

        expect(getByText('Test')).toBeTruthy();
        expect(getByLabelText('test_id')).toBeTruthy();
        expect(getByRole('button', { name: 'Get Status' })).toBeTruthy();
        expect(getByRole('button', { name: 'Submit' })).toBeTruthy();
    });

    test('navbar reset nonce restores Run Test form defaults', () => {
        const { getByLabelText, store } = renderWithProvider(<TestTab />);

        const testIdInput = getByLabelText('test_id') as HTMLInputElement;
        fireEvent.change(testIdInput, { target: { value: 'custom_id' } });
        expect(testIdInput.value).toBe('custom_id');

        store.dispatch(uiActions.setUi({ testTabResetNonce: Date.now() }));

        expect((getByLabelText('test_id') as HTMLInputElement).value).toBe('test_1');
        expect((getByLabelText('External API host') as HTMLInputElement).value).toBe('34.71.3.151');
    });

    test('does not fetch test-results until after a successful Submit enables the session', async () => {
        const fetchSpy = vi.mocked(globalThis.fetch);

        renderWithProvider(<TestTab />, {
            swarm: { ...swarmStateMock, state: SWARM_STATE.STOPPED },
        });

        await new Promise(resolve => setTimeout(resolve, 150));

        const testResultsCalls = fetchSpy.mock.calls.filter(args =>
            String(args[0]).includes('test-results'),
        );
        expect(testResultsCalls.length).toBe(0);
    });
});
