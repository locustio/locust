import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

import { swarmStateMock } from 'test/mocks/swarmState.mock';

global.window.templateArgs = swarmStateMock;
window.matchMedia = vi.fn().mockImplementation(() => ({
  matches: false,
}));

afterEach(() => {
  cleanup();
});
