import { describe, expect, test } from 'vitest';

import TestTab from 'components/TestTab/TestTab';
import { renderWithProvider } from 'test/testUtils';

describe('TestTab', () => {
    test('renders request form inputs', () => {
        const { getByLabelText, getByText, getByRole } = renderWithProvider(<TestTab />);

        expect(getByText('Test')).toBeTruthy();
        expect(getByLabelText('test_id')).toBeTruthy();
        expect(getByRole('button', { name: 'Get Status' })).toBeTruthy();
        expect(getByRole('button', { name: 'Submit' })).toBeTruthy();
    });
});
