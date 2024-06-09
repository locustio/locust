import { useEffect, useState, useRef } from 'react';
import {
  init,
  registerTheme,
  dispose,
  ECharts,
  EChartsOption,
  DefaultLabelFormatterCallbackParams,
  connect,
  TooltipComponentOption,
} from 'echarts';

import { IUiState } from 'redux/slice/ui.slice';
import { ICharts } from 'types/ui.types';
import { formatLocaleString, formatLocaleTime } from 'utils/date';

interface ILine {
  name: string;
  key: keyof ICharts;
}

interface ICreateOptions {
  title: string;
  seriesData: EChartsOption['Series'][];
  charts: ICharts;
  colors?: string[];
}

export interface ILineChartProps {
  title: string;
  lines: ILine[];
  colors?: string[];
}

interface ILineChart extends ILineChartProps {
  charts: ICharts;
}

const CHART_TEXT_COLOR = '#b3c3bc';
const CHART_AXIS_COLOR = '#5b6f66';

registerTheme('locust', {
  backgroundColor: '#27272a',
  textStyle: { color: CHART_TEXT_COLOR },
  title: {
    textStyle: { color: CHART_TEXT_COLOR },
  },
});

const createOptions = ({ charts, title, seriesData, colors }: ICreateOptions) => ({
  legend: {
    icon: 'circle',
    inactiveColor: CHART_TEXT_COLOR,
    textStyle: {
      color: CHART_TEXT_COLOR,
    },
  },
  title: {
    text: title,
    x: 10,
    y: 10,
  },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 50,
    },
  ],
  tooltip: {
    trigger: 'axis',
    formatter: (params: TooltipComponentOption) => {
      if (
        !!params &&
        Array.isArray(params) &&
        params.length > 0 &&
        params.some(param => !!param.value)
      ) {
        return params.reduce(
          (tooltipText, { axisValue, color, seriesName, value }, index) => `
          ${index === 0 ? formatLocaleString(axisValue) : ''}
          ${tooltipText}
          <br>
          <span style="color:${color};">
            ${seriesName}:&nbsp${value}
          </span>
        `,
          '',
        );
      } else {
        return 'No data';
      }
    },
    axisPointer: {
      animation: true,
    },
    textStyle: {
      color: CHART_TEXT_COLOR,
      fontSize: 13,
    },
    backgroundColor: 'rgba(21,35,28, 0.93)',
    borderWidth: 0,
    extraCssText: 'z-index:1;',
  },
  xAxis: {
    type: 'category',
    splitLine: {
      show: false,
    },
    axisLine: {
      lineStyle: {
        color: CHART_AXIS_COLOR,
      },
    },
    axisLabel: {
      formatter: formatLocaleTime,
    },
    data: charts.time,
  },
  yAxis: {
    type: 'value',
    boundaryGap: [0, '5%'],
    splitLine: {
      show: false,
    },
    axisLine: {
      lineStyle: {
        color: CHART_AXIS_COLOR,
      },
    },
  },
  series: seriesData,
  grid: { x: 60, y: 70, x2: 40, y2: 40 },
  color: colors,
  toolbox: {
    feature: {
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

const getSeriesData = ({ charts, lines }: { charts: IUiState['charts']; lines: ILine[] }) =>
  lines.map(({ key, name }) => ({
    name,
    type: 'line',
    showSymbol: true,
    data: charts[key],
  }));

const createMarkLine = (charts: ICharts) => ({
  symbol: 'none',
  label: {
    formatter: (params: DefaultLabelFormatterCallbackParams) => `Run #${params.dataIndex + 1}`,
  },
  lineStyle: { color: CHART_AXIS_COLOR },
  data: (charts.markers || []).map((timeMarker: string) => ({ xAxis: timeMarker })),
});

export default function LineChart({ charts, title, lines, colors }: ILineChart) {
  const [chart, setChart] = useState<ECharts | null>(null);

  const chartContainer = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainer.current) {
      return;
    }

    const initChart = init(chartContainer.current, 'locust');
    initChart.setOption(
      createOptions({ charts, title, seriesData: getSeriesData({ charts, lines }), colors }),
    );

    const handleChartResize = () => initChart.resize();
    window.addEventListener('resize', handleChartResize);

    initChart.group = 'swarmCharts';
    connect('swarmCharts');

    setChart(initChart);

    return () => {
      dispose(initChart);
      window.removeEventListener('resize', handleChartResize);
    };
  }, [chartContainer]);

  useEffect(() => {
    const isChartDataDefined = lines.every(({ key }) => !!charts[key]);
    if (chart && isChartDataDefined) {
      chart.setOption({
        xAxis: { data: charts.time },
        series: lines.map(({ key }, index) => ({
          data: charts[key],
          ...(index === 0 ? { markLine: createMarkLine(charts) } : {}),
        })),
      });
    }
  }, [charts, chart, lines]);

  return <div ref={chartContainer} style={{ width: '100%', height: '300px' }}></div>;
}
