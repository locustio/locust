import { useEffect, useState, useRef } from 'react';
import {
  init,
  registerTheme,
  dispose,
  ECharts,
  EChartsOption,
  TooltipComponentFormatterCallbackParams,
  DefaultLabelFormatterCallbackParams,
} from 'echarts';
import { connect } from 'react-redux';

import { IUiState } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';
import { ICharts } from 'types/ui.types';

interface ILine {
  name: string;
  key: keyof ICharts;
}

interface ICreateOptions {
  title: string;
  seriesData: EChartsOption['Series'][];
  charts: ICharts;
}

export interface ILineChartProps {
  title: string;
  lines: ILine[];
}

interface ILineChart extends ILineChartProps {
  title: string;
  lines: ILine[];
  charts: ICharts;
}

const createOptions = ({ charts, title, seriesData }: ICreateOptions) => ({
  legend: {
    icon: 'circle',
    inactiveColor: '#b3c3bc',
    textStyle: {
      color: '#b3c3bc',
    },
  },
  title: {
    text: title,
    x: 10,
    y: 10,
  },
  tooltip: {
    trigger: 'axis',
    formatter: (params: TooltipComponentFormatterCallbackParams) => {
      if (
        !!params &&
        Array.isArray(params) &&
        params.length > 0 &&
        params.some(param => !!param.value)
      ) {
        return params.reduce(
          (tooltipText, { color, seriesName, value }) => `
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
      color: '#b3c3bc',
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
        color: '#5b6f66',
      },
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
        color: '#5b6f66',
      },
    },
  },
  series: seriesData,
  grid: { x: 60, y: 70, x2: 40, y2: 40 },
  color: ['#00ca5a', '#ff6d6d'],
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
  lineStyle: { color: '#5b6f66' },
  data: (charts.markers || []).map((timeMarker: string) => ({ xAxis: timeMarker })),
});

registerTheme('locust', {
  backgroundColor: '#27272a',
  xAxis: { lineColor: '#f00' },
  textStyle: { color: '#b3c3bc' },
  title: {
    textStyle: { color: '#b3c3bc' },
  },
});

function LineChart({ charts, title, lines }: ILineChart) {
  const [chart, setChart] = useState<ECharts | null>(null);

  const chartContainer = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainer.current) {
      return;
    }

    const initChart = init(chartContainer.current, 'locust');
    initChart.setOption(
      createOptions({ charts, title, seriesData: getSeriesData({ charts, lines }) }),
    );

    setChart(initChart);

    return () => {
      dispose(initChart);
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

const storeConnector = ({ ui: { charts } }: IRootState) => ({ charts });

export default connect(storeConnector)(LineChart);
