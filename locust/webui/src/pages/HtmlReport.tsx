import { Box, Typography, Container, Link } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { combineReducers, configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';

import { ExceptionsTable } from 'components/ExceptionsTable/ExceptionsTable';
import { FailuresTable } from 'components/FailuresTable/FailuresTable';
import ResponseTimeTable from 'components/ResponseTimeTable/ResponseTimeTable';
import { StatsTable } from 'components/StatsTable/StatsTable';
import { SwarmCharts } from 'components/SwarmCharts/SwarmCharts';
import { SwarmRatios } from 'components/SwarmRatios/SwarmRatios';
import { INITIAL_THEME } from 'constants/theme';
import theme from 'redux/slice/theme.slice';
import createTheme from 'styles/theme';
import { IReport } from 'types/swarm.types';
import { formatLocaleString } from 'utils/date';

const muiTheme = createTheme(window.theme || INITIAL_THEME);
const isDarkMode = (window.theme || INITIAL_THEME) === 'dark';

const statsReportTableStructure = [
  { key: 'method', title: 'Type' },
  { key: 'name', title: 'Name' },
  { key: 'numRequests', title: '# Requests' },
  { key: 'numFailures', title: '# Fails' },
  { key: 'avgResponseTime', title: 'Average (ms)', round: 2 },
  { key: 'minResponseTime', title: 'Min (ms)' },
  { key: 'maxResponseTime', title: 'Max (ms)' },
  { key: 'avgContentLength', title: 'Average size (bytes)', round: 2 },
  { key: 'totalRps', title: 'RPS', round: 2 },
  { key: 'totalFailPerSec', title: 'Failures/s', round: 2 },
];

const reportStore = configureStore({
  reducer: combineReducers({ theme }),
  preloadedState: { theme: { isDarkMode } },
});

export default function HtmlReport({
  locustfile,
  showDownloadLink,
  startTime,
  endTime,
  charts,
  host,
  exceptionsStatistics,
  requestsStatistics,
  failuresStatistics,
  responseTimeStatistics,
  tasks,
}: IReport) {
  return (
    <Provider store={reportStore}>
      <ThemeProvider theme={muiTheme}>
        <CssBaseline />

        <Container maxWidth='lg' sx={{ my: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <Typography
              component='h1'
              noWrap
              sx={{
                fontWeight: 700,
              }}
              variant='h3'
            >
              Locust Test Report
            </Typography>
            {showDownloadLink && (
              <Link href={`?download=1&theme=${window.theme}`}>Download the Report</Link>
            )}
          </Box>
          <Box sx={{ my: 2 }}>
            <Box sx={{ display: 'flex', columnGap: 0.5 }}>
              <Typography fontWeight={600}>During:</Typography>
              <Typography>
                {formatLocaleString(startTime)} - {formatLocaleString(endTime)}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', columnGap: 0.5 }}>
              <Typography fontWeight={600}>Target Host:</Typography>
              <Typography>{host || 'None'}</Typography>
            </Box>

            <Box sx={{ display: 'flex', columnGap: 0.5 }}>
              <Typography fontWeight={600}>Script:</Typography>
              <Typography>{locustfile}</Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4 }}>
            <Box>
              <Typography component='h2' mb={1} noWrap variant='h4'>
                Request Statistics
              </Typography>
              <StatsTable stats={requestsStatistics} tableStructure={statsReportTableStructure} />
            </Box>
            {!!responseTimeStatistics.length && (
              <Box>
                <Typography component='h2' mb={1} noWrap variant='h4'>
                  Response Time Statistics
                </Typography>
                <ResponseTimeTable responseTimes={responseTimeStatistics} />
              </Box>
            )}
            <Box>
              <Typography component='h2' mb={1} noWrap variant='h4'>
                Failures Statistics
              </Typography>
              <FailuresTable errors={failuresStatistics} />
            </Box>
            {!!exceptionsStatistics.length && (
              <Box>
                <Typography component='h2' mb={1} noWrap variant='h4'>
                  Exceptions Statistics
                </Typography>
                <ExceptionsTable exceptions={exceptionsStatistics} />
              </Box>
            )}

            <Box>
              <Typography component='h2' mb={1} noWrap variant='h4'>
                Charts
              </Typography>
              <SwarmCharts charts={charts} />
            </Box>
            <Box>
              <Typography component='h2' mb={1} noWrap variant='h4'>
                Final ratio
              </Typography>
              <SwarmRatios ratios={tasks} />
            </Box>
          </Box>
        </Container>
      </ThemeProvider>
    </Provider>
  );
}
