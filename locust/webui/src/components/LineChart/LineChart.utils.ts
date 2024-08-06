import {
  ECharts,
  DefaultLabelFormatterCallbackParams,
  LineSeriesOption,
  YAXisComponentOption,
  ScatterSeriesOption,
} from 'echarts';

import { CHART_THEME } from 'components/LineChart/LineChart.constants';
import {
  ILineChartTimeAxis,
  ILineChart,
  ILineChartZoomEvent,
  ILineChartTooltipFormatterParams,
} from 'components/LineChart/LineChart.types';
import { ICharts } from 'types/ui.types';
import { formatLocaleString, formatLocaleTime } from 'utils/date';

export const getSeriesData = <ChartType>({
  charts,
  lines,
  scatterplot,
}: Pick<ILineChart<ChartType>, 'charts' | 'lines' | 'scatterplot'>):
  | LineSeriesOption[]
  | ScatterSeriesOption[] =>
  lines.map(({ key, name }) => ({
    symbolSize: 4,
    type: (scatterplot ? 'scatter' : 'line') as any,
    name,
    data: charts[key] as LineSeriesOption['data'],
  }));

const Y_AXIS_CONFIG = {
  type: 'value',
  boundaryGap: [0, '5%'],
};

const createYAxis = <ChartType>({
  splitAxis,
  yAxisLabels,
}: Pick<ILineChart<ChartType>, 'splitAxis' | 'yAxisLabels'>):
  | YAXisComponentOption
  | YAXisComponentOption[] => {
  if (splitAxis && (!yAxisLabels || Array.isArray(yAxisLabels))) {
    return Array(2)
      .fill(Y_AXIS_CONFIG)
      .map((config, index) => ({
        ...config,
        ...(yAxisLabels ? { name: yAxisLabels[index] } : {}),
      }));
  }

  return {
    ...Y_AXIS_CONFIG,
    ...(yAxisLabels ? { name: yAxisLabels } : {}),
  } as YAXisComponentOption;
};

export const createOptions = <ChartType extends ILineChartTimeAxis>({
  charts,
  title,
  lines,
  colors,
  chartValueFormatter,
  splitAxis,
  yAxisLabels,
  scatterplot,
}: ILineChart<ChartType>) => ({
  title: { text: title },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 100,
    },
  ],
  tooltip: {
    trigger: 'axis',
    formatter: (params?: ILineChartTooltipFormatterParams[] | null) => {
      if (Array.isArray(params) && params.length > 0 && params.some(param => !!param.value)) {
        return params.reduce(
          (tooltipText, { axisValue, color, seriesName, value }, index) =>
            `
            ${index === 0 ? formatLocaleString(axisValue) : ''}
            ${tooltipText}
            <br>
            <span style="color:${color};">
              ${seriesName}:&nbsp${chartValueFormatter ? chartValueFormatter(value) : value}
            </span>
          `,
          '',
        );
      } else {
        return 'No data';
      }
    },
    borderWidth: 0,
  },
  xAxis: {
    type: 'category',
    axisLabel: { formatter: formatLocaleTime },
    data: charts.time,
  },
  grid: { left: 40, right: splitAxis ? 40 : 10 },
  yAxis: createYAxis({ splitAxis, yAxisLabels }),
  series: getSeriesData<ChartType>({ charts, lines, scatterplot }),
  color: colors,
  toolbox: {
    feature: {
      dataZoom: {
        show: true,
        title: {
          zoom: 'Zoom Select',
          back: 'Zoom Reset',
        },
      },
      saveAsImage: {
        name: title.replace(/\s+/g, '_').toLowerCase() + '_' + new Date().getTime() / 1000,
        title: 'Download as PNG',
        emphasis: {
          iconStyle: {
            textPosition: 'left',
          },
        },
      },
    },
  },
});

export const createMarkLine = <ChartType extends Pick<ICharts, 'markers'>>(
  charts: ChartType,
  isDarkMode: boolean,
) => ({
  symbol: 'none',
  label: {
    formatter: (params: DefaultLabelFormatterCallbackParams) => `Run #${params.dataIndex + 1}`,
  },
  lineStyle: { color: isDarkMode ? CHART_THEME.DARK.axisColor : CHART_THEME.LIGHT.axisColor },
  data: (charts.markers || []).map((timeMarker: string) => ({ xAxis: timeMarker })),
});

export const onChartZoom = (chart: ECharts) => (datazoom: unknown) => {
  const { batch } = datazoom as ILineChartZoomEvent;
  if (!batch) {
    return;
  }

  const [{ start, end }] = batch;
  const isZoomed = start > 0 && end < 100;

  chart.setOption({
    dataZoom: [
      {
        type: 'inside',
        start,
        end,
      },
      {
        type: 'slider',
        show: isZoomed,
        start,
        end,
      },
    ],
  });
};
