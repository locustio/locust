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
  currentRps: number;
  currentFailPerSec: number;
  userCount: number;
  time: string;
  currentResponseTimePercentiles: {
    [key: `responseTimePercentile${number}`]: number | null;
  };
  totalAvgResponseTime: number;
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

export interface IReportTemplateArgs extends IReport {
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
