import { useRef, useState } from 'react';
import { Box, Link, List, ListItem } from '@mui/material';
import type { ECharts } from 'echarts';
import { connect } from 'react-redux';

import SwarmCharts, { SWARM_CHART_COUNT } from 'components/SwarmCharts/SwarmCharts';
import { THEME_MODE } from 'constants/theme';
import { useSelector } from 'redux/hooks';
import { IRootState } from 'redux/store';
import { ISwarmState } from 'types/swarm.types';
import { ICharts } from 'types/ui.types';

const CHART_EXPORT_WIDTH = 1200;
const CHART_EXPORT_PIXEL_RATIO = 3;
const CHART_EXPORT_GROUP = 'swarmReportCharts';

type ExportableChart = ECharts & {
  getConnectedDataURL?: (options: Record<string, unknown>) => string;
  getDataURL: (options: Record<string, unknown>) => string;
};

const hasClientChartData = (charts: ICharts) =>
  Boolean(
    charts &&
      [
        charts.currentRps,
        charts.currentFailPerSec,
        charts.totalAvgResponseTime,
        charts.userCount,
      ].some(series => Array.isArray(series) && series.length > 0),
  );

const constructChartsPngFilename = () =>
  `Locust_charts_${new Date().toISOString().replace(/[:.]/g, '-')}.png`;

const downloadDataUrl = (dataUrl: string, filename: string) => {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const chartBackgroundColor = (isDarkMode: boolean) => (isDarkMode ? '#121212' : '#ffffff');

function ChartsPngDownload({ charts, isDarkMode }: { charts: ICharts; isDarkMode: boolean }) {
  const chartRefs = useRef<(ECharts | null)[]>([]);
  const [readyChartCount, setReadyChartCount] = useState(0);
  const hasData = hasClientChartData(charts);

  if (!hasData) {
    return null;
  }

  const onChartReady = (chart: ECharts, index: number) => {
    if (chartRefs.current[index] === chart) {
      return;
    }

    chartRefs.current[index] = chart;
    setReadyChartCount(chartRefs.current.filter(Boolean).length);
  };

  const onDownloadChartsPng = (event: React.MouseEvent<HTMLElement>) => {
    event.preventDefault();

    if (readyChartCount < SWARM_CHART_COUNT) {
      return;
    }

    const chart = chartRefs.current.find(Boolean) as ExportableChart | undefined;
    if (!chart) {
      return;
    }

    const exportOptions = {
      type: 'png',
      pixelRatio: CHART_EXPORT_PIXEL_RATIO,
      backgroundColor: chartBackgroundColor(isDarkMode),
      excludeComponents: ['toolbox'],
    };
    const dataUrl = chart.getConnectedDataURL
      ? chart.getConnectedDataURL(exportOptions)
      : chart.getDataURL(exportOptions);

    downloadDataUrl(dataUrl, constructChartsPngFilename());
  };

  return (
    <>
      <Link component='button' onClick={onDownloadChartsPng} type='button'>
        Download charts PNG
      </Link>
      <Box
        aria-hidden
        sx={{
          height: SWARM_CHART_COUNT * 300,
          left: -10000,
          opacity: 0,
          overflow: 'hidden',
          pointerEvents: 'none',
          position: 'fixed',
          top: 0,
          width: CHART_EXPORT_WIDTH,
        }}
      >
        <SwarmCharts
          chartGroup={CHART_EXPORT_GROUP}
          charts={charts}
          isDarkMode={isDarkMode}
          onChartReady={onChartReady}
        />
      </Box>
    </>
  );
}

function Reports({
  charts,
  extendedCsvFiles,
  statsHistoryEnabled,
}: Pick<ISwarmState, 'extendedCsvFiles' | 'statsHistoryEnabled'> & { charts: ICharts }) {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  return (
    <List sx={{ display: 'flex', flexDirection: 'column' }}>
      <ListItem>
        <Link href='./stats/requests/csv'>Download requests CSV</Link>
      </ListItem>
      {statsHistoryEnabled && (
        <ListItem>
          <Link href='./stats/requests_full_history/csv'>
            Download full request statistics history CSV
          </Link>
        </ListItem>
      )}
      <ListItem>
        <Link href='./stats/failures/csv'>Download failures CSV</Link>
      </ListItem>
      <ListItem>
        <Link href='./exceptions/csv'>Download exceptions CSV</Link>
      </ListItem>
      <ListItem>
        <Link
          href={`./stats/report?theme=${isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT}`}
          target='_blank'
        >
          Download Report
        </Link>
      </ListItem>
      {hasClientChartData(charts) && (
        <ListItem>
          <ChartsPngDownload charts={charts} isDarkMode={isDarkMode} />
        </ListItem>
      )}
      {extendedCsvFiles &&
        extendedCsvFiles.map(({ href, title }, index) => (
          <ListItem key={`extended-csv-${index}`}>
            <Link href={href}>{title}</Link>
          </ListItem>
        ))}
    </List>
  );
}

const storeConnector = ({
  swarm: { extendedCsvFiles, statsHistoryEnabled },
  ui: { charts },
}: IRootState) => ({
  charts,
  extendedCsvFiles,
  statsHistoryEnabled,
});

export default connect(storeConnector)(Reports);
