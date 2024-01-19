import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, vi } from 'vitest';

import { TEST_BASE_API } from 'test/constants';
import { swarmStateMock } from 'test/mocks/swarmState.mock';
import 'vitest-webgl-canvas-mock';

global.window.templateArgs = swarmStateMock;
window.matchMedia = vi.fn().mockImplementation(() => ({
  matches: false,
}));

afterEach(() => {
  cleanup();
});

vi.mock('@reduxjs/toolkit/query/react', async () => {
  const actual = (await vi.importActual('@reduxjs/toolkit/query/react')) as { [key: string]: any };

  return { ...actual, fetchBaseQuery: () => actual.fetchBaseQuery({ baseUrl: TEST_BASE_API }) };
});

vi.mock('echarts', async () => {
  const actual = (await vi.importActual('echarts')) as { [key: string]: any };

  return { ...actual, init: (...args: any[]) => actual.init(...args, { width: 100, height: 100 }) };
});

afterAll(() => {
  vi.clearAllMocks();
});
