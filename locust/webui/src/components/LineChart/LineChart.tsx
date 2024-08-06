import { useEffect, useState, useRef } from 'react';
import { init, dispose, ECharts, connect } from 'echarts';

import { CHART_THEME } from 'components/LineChart/LineChart.constants';
import {
  ILineChartTimeAxis,
  ILineChart,
  ILineChartMarkers,
} from 'components/LineChart/LineChart.types';
import {
  createMarkLine,
  createOptions,
  getSeriesData,
  onChartZoom,
} from 'components/LineChart/LineChart.utils';
import { useSelector } from 'redux/hooks';

interface IBaseChartType extends ILineChartTimeAxis, ILineChartMarkers {}

export default function LineChart<ChartType extends IBaseChartType>({
  charts,
  title,
  lines,
  colors,
  chartValueFormatter,
  splitAxis,
  yAxisLabels,
}: ILineChart<ChartType>) {
  const [chart, setChart] = useState<ECharts | null>(null);
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  const chartContainer = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainer.current) {
      return;
    }

    const initChart = init(chartContainer.current);

    initChart.setOption(
      createOptions<ChartType>({
        charts,
        title,
        lines,
        colors,
        chartValueFormatter,
        splitAxis,
        yAxisLabels,
      }),
    );
    initChart.on('datazoom', onChartZoom(initChart));

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
        series: lines.map(({ key, yAxisIndex, ...echartsOptions }, index) => ({
          ...echartsOptions,
          data: charts[key],
          ...(splitAxis ? { yAxisIndex: yAxisIndex || index } : {}),
          ...(index === 0 ? { markLine: createMarkLine<ChartType>(charts, isDarkMode) } : {}),
        })),
      });
    }
  }, [charts, chart, lines, isDarkMode]);

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
      chart.setOption({
        series: getSeriesData<ChartType>({ charts, lines }),
      });
    }
  }, [lines]);

  return <div ref={chartContainer} style={{ width: '100%', height: '300px' }}></div>;
}
