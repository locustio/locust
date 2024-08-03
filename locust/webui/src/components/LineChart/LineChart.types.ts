export interface ILine<ChartType> {
  name: string;
  key: keyof ChartType;
  stack?: string;
  areaStyle?: { [key: string]: any };
  yAxisIndex?: number;
}

export interface ILineChart<ChartType> {
  charts: ChartType;
  title: string;
  lines: ILine<ChartType>[];
  colors?: string[];
  chartValueFormatter?: (value: string | number | string[] | number[]) => string | number;
  splitAxis?: boolean;
  yAxisLabels?: string | [string, string];
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
