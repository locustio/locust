import { useEffect, useRef, useState } from 'react';
import type { MouseEvent } from 'react';
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
const REPORT_DOWNLOAD_FALLBACK_FILENAME = 'Locust_report.html';
const REPORT_MODULE_SCRIPT_MARKER = '<script type="module" src=';
const REPORT_TEMPLATE_ARGS_ASSIGNMENT = 'window.templateArgs = ';
const REPORT_THEME_ASSIGNMENT_PATTERN = /\n\s*window\.theme\s*=/;

type ExportableChart = ECharts & {
  getConnectedDataURL?: (options: Record<string, unknown>) => string;
  getDataURL: (options: Record<string, unknown>) => string;
};

export const hasClientChartData = (charts: ICharts) =>
  Boolean(
    charts &&
      [
        charts.currentRps,
        charts.currentFailPerSec,
        charts.totalAvgResponseTime,
        charts.userCount,
      ].some(series => Array.isArray(series) && series.length > 0),
  );

const constructReportUrl = (isDarkMode: boolean, shouldDownload = false) =>
  `./stats/report?${shouldDownload ? 'download=1&' : ''}theme=${
    isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT
  }`;

export const filenameFromContentDisposition = (contentDisposition: string | null) => {
  if (!contentDisposition) {
    return REPORT_DOWNLOAD_FALLBACK_FILENAME;
  }

  const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);

  return filenameMatch?.[1] || REPORT_DOWNLOAD_FALLBACK_FILENAME;
};

export const injectChartsPngIntoReportHtml = (reportHtml: string, chartsPng: string) => {
  const templateArgsAssignmentStart = reportHtml.indexOf(REPORT_TEMPLATE_ARGS_ASSIGNMENT);
  const templateArgsValueStart =
    templateArgsAssignmentStart === -1
      ? -1
      : templateArgsAssignmentStart + REPORT_TEMPLATE_ARGS_ASSIGNMENT.length;
  const templateArgsRemainder =
    templateArgsValueStart === -1 ? '' : reportHtml.slice(templateArgsValueStart);
  const templateArgsEndMatch = templateArgsRemainder.match(REPORT_THEME_ASSIGNMENT_PATTERN);

  if (templateArgsValueStart !== -1 && templateArgsEndMatch?.index !== undefined) {
    try {
      const templateArgsValueEnd = templateArgsValueStart + templateArgsEndMatch.index;
      const templateArgs = JSON.parse(
        reportHtml.slice(templateArgsValueStart, templateArgsValueEnd).trim(),
      );
      const updatedTemplateArgs = JSON.stringify({
        ...templateArgs,
        charts_png: chartsPng,
        history: [],
      });

      return `${reportHtml.slice(0, templateArgsValueStart)}${updatedTemplateArgs}${reportHtml.slice(
        templateArgsValueEnd,
      )}`;
    } catch {
      // Fall back to adding a small pre-module script if the report template changes.
    }
  }

  const script = `<script>window.templateArgs = Object.assign({}, window.templateArgs, ${JSON.stringify(
    { charts_png: chartsPng },
  )})</script>`;

  if (reportHtml.includes(REPORT_MODULE_SCRIPT_MARKER)) {
    return reportHtml.replace(
      REPORT_MODULE_SCRIPT_MARKER,
      `${script}\n    ${REPORT_MODULE_SCRIPT_MARKER}`,
    );
  }

  if (reportHtml.includes('</body>')) {
    return reportHtml.replace('</body>', `${script}\n  </body>`);
  }

  return `${reportHtml}\n${script}`;
};

const downloadHtml = (html: string, filename: string) => {
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

const downloadReportWithChartsPng = async (reportDownloadUrl: string, chartsPng: string) => {
  const response = await fetch(reportDownloadUrl);

  if (!response.ok) {
    throw new Error('Unable to download report');
  }

  const reportHtml = await response.text();
  const filename = filenameFromContentDisposition(response.headers.get('Content-Disposition'));

  downloadHtml(injectChartsPngIntoReportHtml(reportHtml, chartsPng), filename);
};

const chartBackgroundColor = (isDarkMode: boolean) => (isDarkMode ? '#121212' : '#ffffff');

function ReportDownload({ charts, isDarkMode }: { charts: ICharts; isDarkMode: boolean }) {
  const chartRefs = useRef<(ECharts | null)[]>([]);
  const isDownloadingReport = useRef(false);
  const [isPreparingReport, setIsPreparingReport] = useState(false);
  const [readyChartCount, setReadyChartCount] = useState(0);
  const hasData = hasClientChartData(charts);
  const reportHref = constructReportUrl(isDarkMode);
  const reportDownloadHref = constructReportUrl(isDarkMode, true);

  useEffect(() => {
    if (
      !isPreparingReport ||
      isDownloadingReport.current ||
      readyChartCount < SWARM_CHART_COUNT
    ) {
      return;
    }

    const chart = chartRefs.current.find(Boolean) as ExportableChart | undefined;
    if (!chart) {
      setIsPreparingReport(false);
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

    isDownloadingReport.current = true;

    void downloadReportWithChartsPng(reportDownloadHref, dataUrl)
      .catch(() => {
        window.open(reportHref, '_blank');
      })
      .finally(() => {
        isDownloadingReport.current = false;
        setIsPreparingReport(false);
      });
  }, [isDarkMode, isPreparingReport, readyChartCount, reportDownloadHref, reportHref]);

  const onChartReady = (chart: ECharts, index: number) => {
    if (chartRefs.current[index] === chart) {
      return;
    }

    chartRefs.current[index] = chart;
    setReadyChartCount(chartRefs.current.filter(Boolean).length);
  };

  const onDownloadReport = (event: MouseEvent<HTMLElement>) => {
    if (!hasData) {
      return;
    }

    event.preventDefault();

    if (isPreparingReport) {
      return;
    }

    chartRefs.current = [];
    setReadyChartCount(0);
    setIsPreparingReport(true);
  };

  return (
    <>
      <Link href={reportHref} onClick={onDownloadReport} target='_blank'>
        Download Report
      </Link>
      {isPreparingReport && (
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
      )}
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
        <ReportDownload charts={charts} isDarkMode={isDarkMode} />
      </ListItem>
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
