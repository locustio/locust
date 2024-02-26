import { IReport } from 'types/swarm.types';
import { ISwarmRatios } from 'types/ui.types';

export const percentilesToChart = [0.5, 0.95];
export const percentilesToStatistics = [0.5, 0.95, 0.99];

export const swarmStateMock = {
  availableShapeClasses: ['Default'],
  availableUserClasses: ['ExampleClass'],
  availableUserTasks: { ExampleClass: ['ExampleTask'] },
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
  percentilesToStatistics: percentilesToStatistics,
  showUserclassPicker: false,
  spawnRate: null,
  state: 'ready',
  percentilesToChart: percentilesToChart,
  statsHistoryEnabled: false,
  tasks: '{}',
  userCount: 0,
  version: '2.15.0',
  workerCount: 0,
  users: {},
};

export const swarmReportMock: IReport = {
  locustfile: 'locustfile.py',
  showDownloadLink: true,
  startTime: '2024-02-26 12:13:26',
  endTime: '2024-02-26 12:13:26',
  host: 'http://0.0.0.0:8089/',
  exceptionsStatistics: [],
  requestsStatistics: [],
  failuresStatistics: [],
  responseTimeStatistics: [],
  tasks: {} as ISwarmRatios,
  charts: {
    currentRps: [0],
    currentFailPerSec: [0],
    totalAvgResponseTime: [0],
    userCount: [0],
    time: [''],
  },
};
