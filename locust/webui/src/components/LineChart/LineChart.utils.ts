import { ECharts, DefaultLabelFormatterCallbackParams, TooltipComponentOption } from 'echarts';

import { ICharts } from 'types/ui.types';
import { formatLocaleString, formatLocaleTime } from 'utils/date';

import { CHART_THEME } from './LineChart.constants';
import { ILineChartTimeAxis, ILineChart, ILineChartZoomEvent } from './LineChart.types';

export const getSeriesData = <ChartType>({
  charts,
  lines,
}: Pick<ILineChart<ChartType>, 'charts' | 'lines'>) =>
  lines.map(({ key, name }) => ({
    type: 'line',
    name,
    data: charts[key],
  }));

const Y_AXIS_CONFIG = {
  type: 'value',
  boundaryGap: [0, '5%'],
};

const createYAxis = <ChartType>({
  splitAxis,
  yAxisLabels,
}: Pick<ILineChart<ChartType>, 'splitAxis' | 'yAxisLabels'>) => {
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
  };
};

export const createOptions = <ChartType extends ILineChartTimeAxis>({
  charts,
  title,
  lines,
  colors,
  chartValueFormatter,
  splitAxis,
  yAxisLabels,
}: ILineChart<ChartType>) => ({
  title: {
    text: title,
    x: 10,
    y: 10,
  },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 100,
    },
  ],
  tooltip: {
    trigger: 'axis',
    formatter: (params: TooltipComponentOption) => {
      if (Array.isArray(params) && params.length > 0 && params.some(param => !!param.value)) {
        return params.reduce(
          (tooltipText, { axisValue, color, seriesName, value }, index) => `
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
  yAxis: createYAxis({ splitAxis, yAxisLabels }),
  series: getSeriesData<ChartType>({ charts, lines }),
  grid: { x: 60, y: 70, x2: 40, y2: 40 },
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
