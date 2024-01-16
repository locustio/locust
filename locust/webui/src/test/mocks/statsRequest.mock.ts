export const statsResponseMock = {
  current_response_time_percentiles: {
    'response_time_percentile_0.5': 2,
    'response_time_percentile_0.95': 2,
  },
  errors: [
    {
      error: 'ConnectionRefusedError(111, &#x27;Connection refused&#x27;)',
      method: 'GET',
      name: '/',
      occurrences: 12652,
    },
  ],
  fail_ratio: 1.0,
  state: 'running',
  stats: [
    {
      avg_content_length: 0.0,
      avg_response_time: 0.41064205516736735,
      current_fail_per_sec: 1932.5,
      current_rps: 1932.5,
      max_response_time: 22.0,
      median_response_time: 0.35867700034941663,
      method: 'GET',
      min_response_time: 0.0,
      name: '/',
      "response_time_percentile_0.9": 0,
      "response_time_percentile_0.99": 1,
      num_failures: 12652,
      num_requests: 12652,
      safe_name: '/',
    },
    {
      avg_content_length: 0.0,
      avg_response_time: 0.41064205516736735,
      current_fail_per_sec: 1932.5,
      current_rps: 1932.5,
      max_response_time: 22.0,
      median_response_time: 0.35867700034941663,
      method: '',
      min_response_time: 0.0,
      name: 'Aggregated',
      "response_time_percentile_0.9": 0,
      "response_time_percentile_0.99": 1,
      num_failures: 12652,
      num_requests: 12652,
      safe_name: 'Aggregated',
    },
  ],
  total_avg_response_time: 0.41064205516736735,
  total_fail_per_sec: 1932.5,
  total_rps: 1932.5,
  user_count: 1,
};

export const ratiosResponseMock = {
  per_class: {
    Example: {
      ratio: 1.0,
      tasks: {
        ExampleTest: {
          ratio: 1.0,
          tasks: {
            example: {
              ratio: 1.0,
            },
          },
        },
      },
    },
  },
  total: {
    Example: {
      ratio: 1.0,
      tasks: {
        ExampleTest: {
          ratio: 1.0,
          tasks: {
            example: {
              ratio: 1.0,
            },
          },
        },
      },
    },
  },
};

export const exceptionsResponseMock = {
  exceptions: [
    {
      count: 8813,
      msg: 'Test exception',
      nodes: 'local',
      traceback: 'Test',
    },
  ],
};

export const mockDate = new Date(1970, 1);

export const statsResponseTransformed = {
  totalRps: 1932.5,
  failRatio: 100,
  stats: [
    {
      avgContentLength: 0,
      avgResponseTime: 0.41064205516736735,
      currentFailPerSec: 1932.5,
      currentRps: 1932.5,
      maxResponseTime: 22,
      medianResponseTime: 0.35867700034941663,
      method: 'GET',
      minResponseTime: 0,
      name: '/',
      "responseTimePercentile0.9": 0,
      "responseTimePercentile0.99": 1,
      numFailures: 12652,
      numRequests: 12652,
      safeName: '/',
    },
    {
      avgContentLength: 0,
      avgResponseTime: 0.41064205516736735,
      currentFailPerSec: 1932.5,
      currentRps: 1932.5,
      maxResponseTime: 22,
      medianResponseTime: 0.35867700034941663,
      method: '',
      minResponseTime: 0,
      name: 'Aggregated',
      "responseTimePercentile0.9": 0,
      "responseTimePercentile0.99": 1,
      numFailures: 12652,
      numRequests: 12652,
      safeName: 'Aggregated',
    },
  ],
  errors: [
    {
      error: 'ConnectionRefusedError(111, &#x27;Connection refused&#x27;)',
      method: 'GET',
      name: '/',
      occurrences: 12652,
    },
  ],
  exceptions: exceptionsResponseMock.exceptions,
  extendedStats: undefined,
  charts: {
    'responseTimePercentile0.5': [2],
    'responseTimePercentile0.95': [2],
    currentRps: [1932.5],
    currentFailPerSec: [1932.5],
    userCount: [1],
    totalAvgResponseTime: [0.41],
    time: [mockDate.toLocaleTimeString()],
  },
  ratios: {
    perClass: {
      Example: {
        ratio: 1,
        tasks: { ExampleTest: { ratio: 1, tasks: { example: { ratio: 1 } } } },
      },
    },
    total: {
      Example: {
        ratio: 1,
        tasks: { ExampleTest: { ratio: 1, tasks: { example: { ratio: 1 } } } },
      },
    },
  },
  userCount: 1,
  workers: undefined,
};
