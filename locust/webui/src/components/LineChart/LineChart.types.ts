export interface ILine<ChartType> {
  name: string;
  key: keyof ChartType;
}

export interface ILineChart<ChartType> {
  charts: ChartType;
  title: string;
  lines: ILine<ChartType>[];
  colors?: string[];
  chartValueFormatter?: (value: string | number | string[] | number[]) => string | number;
}

export interface ILineChartZoomEvent {
  batch?: { start: number; end: number }[];
}

export interface ILineChartTimeAxis {
  time: string[];
}

export interface ILineChartMarkers {
  markers?: string[];
}
