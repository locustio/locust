import { Box, Link, Typography } from '@mui/material';

import Markdown from 'components/Markdown/Markdown';
import { useSelector } from 'redux/hooks';

const firstParagraph = `
Ready to take your load tests to the next level? With [Locust Cloud](locust.cloud), we take care of everything!
\n
Whether your doing small load, or needing to generate millions of requests, we take care of the
load generation. Not sure where to start? Get professional load test consultation! We have over 20 years of experience load testing in a wide array of industries!
\n
Locust Cloud comes powered with a suite of features, including advanced graphs, stored testruns, open telemetry, and so much more!
`;

export default function LocustCloudTab() {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Typography component='h2' mb={1} variant='h4'>
          Power Up Your Load Tests!
        </Typography>
        <Markdown content={firstParagraph} />
      </Box>
      <Typography sx={{ mb: 2 }}>
        Our main graphs offer a concise view of the most vital stats, and go further by allowing you
        to dig into data for each requests in your testrun
      </Typography>
      {isDarkMode ? (
        <img src='/assets/graphs-dark.png' width='100%' />
      ) : (
        <img src='/assets/graphs-light.png' width='100%' />
      )}
      <Typography sx={{ mb: 2 }}>
        The testruns tab offers a detailed overview of how your system has performed historically.
        This is particularly useful for ensuring the performance of your system improves or remains
        constant.
      </Typography>
      {isDarkMode ? (
        <img src='/assets/testruns-dark.png' width='100%' />
      ) : (
        <img src='/assets/testruns-light.png' width='100%' />
      )}
      <Typography>
        Vist us at <Link href='https://www.locust.cloud/get-started?plan=basic'>locust.cloud</Link>{' '}
        for a free consultation today!
      </Typography>
    </Box>
  );
}
