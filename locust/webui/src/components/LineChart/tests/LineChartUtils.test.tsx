import { DefaultLabelFormatterCallbackParams, ECharts } from 'echarts';
import { describe, expect, test, vi } from 'vitest';

import { CHART_THEME } from 'components/LineChart/LineChart.constants';
import { ILineChartTooltipFormatterParams } from 'components/LineChart/LineChart.types';
import {
  getSeriesData,
  createOptions,
  createMarkLine,
  onChartZoom,
} from 'components/LineChart/LineChart.utils';
import {
  mockChartLines,
  mockCharts,
  MockChartType,
  mockScatterplotSeriesData,
  mockSeriesData,
  mockTimestamps,
  mockTooltipParams,
} from 'components/LineChart/tests/LineChart.mocks';
import { formatLocaleString } from 'utils/date';

const removeWhitespace = (string: string) => string.replace(/\s+/g, '');

describe('getSeriesData', () => {
  test('should adapt charts to series data', () => {
    const options = getSeriesData<Partial<MockChartType>>({
      charts: mockCharts,
      lines: mockChartLines,
    });

    expect(options).toEqual(mockSeriesData);
  });

  test('should adapt a scatterplot', () => {
    const options = getSeriesData<Partial<MockChartType>>({
      charts: mockCharts,
      lines: mockChartLines,
      scatterplot: true,
    });

    expect(options).toEqual(mockScatterplotSeriesData);
  });
});

describe('createOptions', () => {
  const createOptionsDefaultProps = {
    charts: mockCharts,
    title: 'Test Chart',
    lines: mockChartLines,
    colors: ['#fff'],
  };

  const defaultYAxis = { type: 'value', boundaryGap: [0, '5%'] };
  const yAxisLabels = ['RPS', 'Users'] as string[] as ['string', 'string'];

  test('should create chart options', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect(options.title.text).toBe('Test Chart');
    expect(options.xAxis.type).toBe('time');
    expect(options.xAxis.startValue).toBe(mockCharts.time[0]);
    expect(options.yAxis).toEqual(defaultYAxis);
    expect(options.series).toEqual(mockSeriesData);
    expect(options.color).toEqual(['#fff']);
  });

  test('should not apply any scroll zoom by default', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect((options as any).dataZoom).toBe(undefined);
  });

  test('xAxis should be formatted as expected', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    const formattedValue = options.xAxis.axisLabel.formatter(mockTimestamps[0]);

    expect(formattedValue).toEqual(new Date(mockTimestamps[0]).toLocaleTimeString());
  });

  test('should format the tooltip as expected', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect(removeWhitespace(options.tooltip.formatter([mockTooltipParams[0]]))).toBe(
      removeWhitespace(`
      ${formatLocaleString(mockTooltipParams[0].axisValue)}

      <br>
      <span style="color:${mockTooltipParams[0].color};">
        ${mockTooltipParams[0].seriesName}:&nbsp${mockTooltipParams[0].value[1]}
      </span>
    `),
    );
    expect(options.tooltip.trigger).toBe('axis');
    expect(options.tooltip.borderWidth).toBe(0);
  });

  test('should format the tooltip with multiple params', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect(removeWhitespace(options.tooltip.formatter(mockTooltipParams))).toBe(
      removeWhitespace(`
      ${formatLocaleString(mockTooltipParams[0].axisValue)}
      <br>
      <span style="color:${mockTooltipParams[0].color};">
        ${mockTooltipParams[0].seriesName}:&nbsp${mockTooltipParams[0].value[1]}
      </span>
      <br>
      <span style="color:${mockTooltipParams[1].color};">
        ${mockTooltipParams[1].seriesName}:&nbsp${mockTooltipParams[1].value[1]}
      </span>
    `),
    );
  });

  test('should format the tooltip with no data when params are not an array, when length is zero, or when array contains no value prop', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect(options.tooltip.formatter(null)).toBe('No data');
    expect(options.tooltip.formatter(undefined)).toBe('No data');
    expect(options.tooltip.formatter([])).toBe('No data');
    expect(options.tooltip.formatter([{} as ILineChartTooltipFormatterParams])).toBe('No data');
  });

  test('should not splitAxis by default', () => {
    const options = createOptions<MockChartType>(createOptionsDefaultProps);

    expect(options.yAxis).toEqual(defaultYAxis);
  });

  test('should splitAxis', () => {
    const options = createOptions<MockChartType>({
      ...createOptionsDefaultProps,
      splitAxis: true,
    });

    expect(options.yAxis).toEqual([defaultYAxis, defaultYAxis]);
  });

  test('should ignore splitAxis if yAxisLabels is not an array', () => {
    const yAxisLabel = 'RPS';
    const options = createOptions<MockChartType>({
      ...createOptionsDefaultProps,
      splitAxis: true,
      yAxisLabels: yAxisLabel,
    });
    const defaultYAxisWithName = {
      ...defaultYAxis,
      name: yAxisLabel,
    };

    expect(options.yAxis).toEqual(defaultYAxisWithName);
  });

  test('should splitAxis with yAxisLabels', () => {
    const options = createOptions<MockChartType>({
      ...createOptionsDefaultProps,
      splitAxis: true,
      yAxisLabels,
    });

    expect(options.yAxis).toEqual([
      { ...defaultYAxis, name: yAxisLabels[0] },
      { ...defaultYAxis, name: yAxisLabels[1] },
    ]);
  });

  test('should create a scatterplot series', () => {
    const options = createOptions<MockChartType>({
      ...createOptionsDefaultProps,
      scatterplot: true,
    });

    expect(options.title.text).toBe('Test Chart');
    expect(options.yAxis).toEqual(defaultYAxis);
    expect(options.xAxis.type).toBe('time');
    expect(options.xAxis.startValue).toBe(mockCharts.time[0]);
    expect(options.series).toEqual(mockScatterplotSeriesData);
    expect(options.color).toEqual(['#fff']);
  });
});

describe('createMarkLine', () => {
  test('should create a mark line', () => {
    const markChartsWithMarkers = {
      ...mockCharts,
      markers: [mockTimestamps[1]],
    };

    const options = createMarkLine(markChartsWithMarkers, false);

    expect(options.symbol).toBe('none');
    expect(options.data).toEqual([{ xAxis: markChartsWithMarkers.markers[0] }]);
    expect(options.lineStyle.color).toBe(CHART_THEME.LIGHT.axisColor);
  });

  test('should create multiple mark lines', () => {
    const markChartsWithMarkers = {
      ...mockCharts,
      markers: [mockTimestamps[1], mockTimestamps[3]],
    };

    const options = createMarkLine(markChartsWithMarkers, false);

    expect(options.data).toEqual([
      { xAxis: markChartsWithMarkers.markers[0] },
      { xAxis: markChartsWithMarkers.markers[1] },
    ]);
  });

  test('should format mark line label', () => {
    const markChartsWithMarkers = {
      ...mockCharts,
      markers: [mockTimestamps[1]],
    };
    const options = createMarkLine(markChartsWithMarkers, false);

    expect(options.label.formatter({ dataIndex: 0 } as DefaultLabelFormatterCallbackParams)).toBe(
      'Run #1',
    );
  });

  test('should use dark mode when isDarkMode', () => {
    const markChartsWithMarkers = {
      ...mockCharts,
      markers: [mockTimestamps[1]],
    };
    const options = createMarkLine(markChartsWithMarkers, true);

    expect(options.lineStyle.color).toBe(CHART_THEME.DARK.axisColor);
  });
});

describe('onChartZoom', () => {
  test('should set dataZoom on chart zoom', () => {
    const mockChart = {
      setOption: vi.fn(),
    } as unknown as ECharts;

    onChartZoom(mockChart)({
      batch: [{ start: 10, end: 90 }],
    });

    expect(mockChart.setOption).toHaveBeenCalledWith({
      dataZoom: [{ type: 'slider', show: true }],
    });
  });

  test('should reset dataZoom on zoom out', () => {
    const mockChart = {
      setOption: vi.fn(),
    } as unknown as ECharts;

    onChartZoom(mockChart)({
      batch: [{ start: 50, end: 60 }],
    });
    onChartZoom(mockChart)({
      batch: [{ start: 0, end: 100 }],
    });

    expect(mockChart.setOption).nthCalledWith(1, {
      dataZoom: [{ type: 'slider', show: true }],
    });
    expect(mockChart.setOption).nthCalledWith(2, {
      dataZoom: [{ type: 'slider', show: false }],
    });
  });
});
