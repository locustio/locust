import { ICharts } from 'types/ui.types';

export interface IExtraOptionParameter {
  choices: string[] | null;
  defaultValue: string | boolean | null;
  helpText: string | null;
  isSecret: boolean;
}

export interface IExtraOptions {
  [key: string]: IExtraOptionParameter;
}

export type History = Omit<ICharts, 'markers'>;
