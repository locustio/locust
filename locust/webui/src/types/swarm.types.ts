import {
  ICharts,
  ISwarmError,
  ISwarmStat,
  IResponseTime,
  ISwarmRatios,
  ISwarmException,
} from 'types/ui.types';

export interface IExtraOptionParameter {
  choices: string[] | null;
  defaultValue: string | number | boolean | null;
  helpText: string | null;
  isSecret: boolean;
}

export interface IExtraOptions {
  [key: string]: IExtraOptionParameter;
}

export interface IHistory {
  currentRps: [string, number];
  currentFailPerSec: [string, number];
  userCount: [string, number];
  currentResponseTimePercentiles: {
    [key: `responseTimePercentile${number}`]: [string, number | null];
  };
  totalAvgResponseTime: [string, number];
  time: string;
}

export interface IReport {
  locustfile: string;
  showDownloadLink: boolean;
  startTime: string;
  endTime: string;
  host: string;
  charts: ICharts;
  requestsStatistics: ISwarmStat[];
  failuresStatistics: ISwarmError[];
  responseTimeStatistics: IResponseTime[];
  exceptionsStatistics: ISwarmException[];
  tasks: ISwarmRatios;
}

export interface IReportTemplateArgs extends Omit<IReport, 'charts'> {
  history: IHistory[];
  isReport?: boolean;
  percentilesToChart: number[];
  percentilesToStatistics: number[];
}

export interface ISwarmUser {
  fixedCount: number;
  host: string;
  weight: number;
  tasks: string[];
}
