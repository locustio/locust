import { SWARM_STATE } from 'constants/swarm';

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
  showUserclassPicker: false,
  spawnRate: null,
  state: SWARM_STATE.READY,
  statsHistoryEnabled: false,
  tasks: '{}',
  userCount: 0,
  version: '2.15.0',
  workerCount: 0,
};
