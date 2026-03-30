import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest';

import TestTab from 'components/TestTab/TestTab';
import { SWARM_STATE } from 'constants/swarm';
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
