import { ICustomInput } from 'types/form.types';
import { ITab } from 'types/tab.types';
import { ITableStructure } from 'types/table.types';
import {
  ICharts,
  ISwarmError,
  ISwarmStat,
  IResponseTime,
  ISwarmRatios,
  ISwarmException,
} from 'types/ui.types';

export interface IExtraOptionParameter extends Omit<ICustomInput, 'name' | 'label'> {
  helpText: string | null;
}

export interface IExtraOptions {
  [key: string]: IExtraOptionParameter;
}

interface IHistory {
  currentRps: [string, number];
  currentFailPerSec: [string, number];
  userCount: [string, number];
  currentResponseTimePercentiles: {
    [key: `responseTimePercentile${number}`]: [string, number | null];
  };
  totalAvgResponseTime: [string, number];
  time: string;
}

export interface ISwarmUser {
  fixedCount: number;
  host: string;
  weight: number;
  tasks: string[];
}

export interface ISwarmState {
  availableShapeClasses: string[];
  availableUserClasses: string[];
  availableUserTasks: { [key: string]: string[] };
  extraOptions: IExtraOptions;
  extendedTabs?: ITab[];
  extendedTables?: { key: string; structure: ITableStructure[] }[];
  extendedCsvFiles?: { href: string; title: string }[];
  history: IHistory[];
  host: string;
  isDistributed: boolean;
  hideCommonOptions?: boolean | null;
  shapeUseCommonOptions?: boolean | null;
  locustfile: string;
  numUsers: number | null;
  overrideHostWarning: boolean;
  missingHostWarning: boolean;
  isHostRequired: boolean;
  percentilesToChart: number[];
  percentilesToStatistics: number[];
  runTime?: string | number;
  showUserclassPicker: boolean;
  spawnRate: number | null;
  state: string;
  statsHistoryEnabled: boolean;
  tasks: string;
  userCount: number | string;
  users: { [key: string]: ISwarmUser };
  version: string;
  workerCount: number;
  profile?: string;
  allProfiles?: string[];
}

export interface IReport {
  locustfile: string;
  showDownloadLink: boolean;
  startTime: string;
  endTime: string;
  duration: string;
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
  profile?: string;
}

export interface ISwarmFormInput
  extends Partial<Pick<ISwarmState, 'host' | 'profile' | 'spawnRate' | 'userCount'>> {
  runTime?: string;
  userClasses?: string[];
  shapeClass?: string;
}

export interface IStartSwarmResponse {
  success: boolean;
  message: string;
  host: string;
}
