import { SWARM_STATE } from 'constants/swarm';

export type SwarmState = (typeof SWARM_STATE)[keyof typeof SWARM_STATE];

export interface ISwarmStat {
  avgContentLength: number;
  avgResponseTime: number;
  currentFailPerSec: number;
  currentRps: number;
  maxResponseTime: number;
  medianResponseTime: number;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  minResponseTime: number;
  name: string;
  [key: `responseTimePercentile${number}`]: number;
  numFailures: number;
  numRequests: number;
  safeName: string;
}

export interface ISwarmError {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  name: string;
  occurrences: number;
}

export interface ISwarmException {
  count: number;
  msg: string;
  nodes: string;
  traceback: string;
}

export interface IResponseTime {
  method: string;
  name: string;
  [percentile: string]: string | number;
}

export interface ISwarmExceptionsResponse {
  exceptions: ISwarmException[];
}

export interface ISwarmWorker {
  cpuUsage: number;
  id: string;
  memoryUsage: number;
  state: (typeof SWARM_STATE)[keyof typeof SWARM_STATE];
  userCount: number;
}

interface NullChartValue {
  value: null;
}

export interface ICharts {
  currentRps: (number | NullChartValue)[];
  currentFailPerSec: (number | NullChartValue)[];
  [key: `responseTimePercentile${number}`]: (number | null | NullChartValue)[];
  totalAvgResponseTime: (number | NullChartValue)[];
  userCount: (number | NullChartValue)[];
  time: string[];
  markers?: string[];
}

export interface IClassRatio {
  [key: string]: {
    ratio: number;
    tasks: IClassRatio;
  };
}

export interface ISwarmRatios {
  perClass: IClassRatio;
  total: IClassRatio;
}

export interface IExtendedStatData {
  name: string;
  safeName: string;
  [key: string]: number | string;
}

export interface IExtendedStat {
  key: string;
  data: IExtendedStatData[];
}

export interface IStatsResponse {
  extendedStats: IExtendedStat[];
  state: SwarmState;
  stats: ISwarmStat[];
  errors: ISwarmError[];
  workers: ISwarmWorker[];
  totalRps: number;
  totalFailPerSec: number;
  totalAvgResponseTime: number;
  currentResponseTimePercentiles: {
    [key: `responseTimePercentile${number}`]: number | null;
  };
  failRatio: number;
  userCount: number;
}

export interface ILogsResponse {
  logs: string[];
}
