export const percentilesToChart = [0.5, 0.95];
export const percentilesToStatics = [0.5, 0.95, 0.99];

export const swarmStateMock = {
  availableShapeClasses: ['Default'],
  availableUserClasses: ['ExampleUser'],
  extraOptions: {},
  history: [],
  host: 'https://localhost',
  isDistributed: false,
  isShape: null,
  locustfile: 'main.py',
  numUsers: null,
  overrideHostWarning: false,
  percentile1: 0.95,
  percentile2: 0.99,
  percentiles_to_statics: percentilesToStatics,
  showUserclassPicker: false,
  spawnRate: null,
  state: 'ready',
  percentilesToChart: percentilesToChart,
  statsHistoryEnabled: false,
  tasks: '{}',
  userCount: 0,
  version: '2.15.0',
  workerCount: 0,
};
