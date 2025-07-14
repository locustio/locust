import { useEffect, useState, useRef } from 'react';
import type { XAXisComponentOption, GridComponentOption, ECharts } from 'echarts';
import { LineChart as BaseLineChart } from 'echarts/charts';
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components';
import { use as echartsUse, init, dispose, connect } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';

import { CHART_THEME } from 'components/LineChart/LineChart.constants';
import {
  ILineChart,
  ILineChartMarkers,
  ILineChartTimeAxis,
} from 'components/LineChart/LineChart.types';
import {
  createMarkLine,
  createOptions,
  getSeriesData,
  onChartZoom,
} from 'components/LineChart/LineChart.utils';

interface IBaseChartType extends ILineChartMarkers, ILineChartTimeAxis {
  [key: string]: any;
}

interface ILineChartProps<ChartType extends IBaseChartType> extends ILineChart<ChartType> {
  shouldReplaceMergeLines?: boolean;
  xAxis?: XAXisComponentOption;
  grid?: GridComponentOption;
  isDarkMode?: boolean;
}

echartsUse([
  BaseLineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer,
]);

export default function LineChart<ChartType extends IBaseChartType>({
  charts,
  title,
  lines,
  colors,
  chartValueFormatter,
  splitAxis,
  yAxisLabels,
  xAxis,
  grid,
  scatterplot,
  shouldReplaceMergeLines = false,
  isDarkMode = false,
}: ILineChartProps<ChartType>) {
  const [chart, setChart] = useState<ECharts | null>(null);

  const chartContainer = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainer.current) {
      return;
    }

    const initChart = init(chartContainer.current) as any;

    initChart.setOption(
      createOptions<ChartType>({
        charts,
        title,
        lines,
        colors,
        chartValueFormatter,
        splitAxis,
        yAxisLabels,
        xAxis,
        grid,
        scatterplot,
      }),
    );
    initChart.on('datazoom', onChartZoom(initChart));

    const handleChartResize = () => {
      initChart.resize();
      initChart.setOption({ xAxis: { splitNumber: window.innerWidth < 900 ? 2 : 7 } });
    };
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
        series: lines.map(({ key, yAxisIndex, ...echartsOptions }, index) => ({
          ...echartsOptions,
          data: charts[key],
          ...(splitAxis ? { yAxisIndex: yAxisIndex || index } : {}),
          ...(index === 0 ? { markLine: createMarkLine<ChartType>(charts) } : {}),
        })),
      });
    }
  }, [charts, chart, lines]);

  useEffect(() => {
    if (chart) {
      const { textColor, axisColor, backgroundColor, splitLine } = isDarkMode
        ? CHART_THEME.DARK
        : CHART_THEME.LIGHT;

      chart.setOption({
        backgroundColor,
        textStyle: { color: textColor },
        title: { textStyle: { color: textColor } },
        legend: {
          icon: 'circle',
          inactiveColor: textColor,
          textStyle: { color: textColor },
        },
        tooltip: { backgroundColor, textStyle: { color: textColor } },
        xAxis: { axisLine: { lineStyle: { color: axisColor } } },
        yAxis: {
          axisLine: { lineStyle: { color: axisColor } },
          splitLine: { lineStyle: { color: splitLine } },
        },
      });
    }
  }, [chart, isDarkMode]);

  useEffect(() => {
    if (chart) {
      chart.setOption(
        {
          series: getSeriesData<ChartType>({ charts, lines, scatterplot }),
        },
        shouldReplaceMergeLines ? { replaceMerge: ['series'] } : undefined,
      );
    }
  }, [lines]);

  return <div ref={chartContainer} style={{ width: '100%', height: '300px' }}></div>;
}
