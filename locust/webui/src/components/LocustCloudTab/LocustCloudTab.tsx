import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { Box, Button, Typography } from '@mui/material';
import { green, grey } from '@mui/material/colors';

import FadeInBox from 'components/FadeInBox';
import Pricing from 'components/LocustCloudTab/Pricing';
import { useSelector } from 'redux/hooks';

export default function LocustCloudTab() {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  return (
    <Box sx={{ mt: 6 }}>
      <FadeInBox sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', rowGap: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            columnGap: 1,
            rowGap: 4,
          }}
        >
          <Typography component='h2' sx={{ textAlign: 'center', fontWeight: 'bold' }} variant='h4'>
            Power Up Your
          </Typography>
          <Typography
            component='h2'
            sx={{ fontWeight: 'bold', color: 'rgb(22, 163, 74)' }}
            variant='h4'
          >
            Locust
          </Typography>
        </Box>
        <Typography
          sx={{ color: isDarkMode ? '#fff' : grey[700], textAlign: 'center' }}
          variant='h6'
        >
          Load testing is hard. Let us take care of the heavy lifting. With Locust Cloud you'll be
          ready to run distributed load tests in minutes.
        </Typography>
        <Box sx={{ display: 'flex', columnGap: 1 }}>
          <Button
            endIcon={<ArrowForwardIcon />}
            sx={{
              textTransform: 'none',
              px: 12,
              py: 1,
              borderRadius: 2,
              backgroundColor: 'rgb(22, 163, 74)',
            }}
            variant='contained'
          >
            Start Free Trial
          </Button>
        </Box>
      </FadeInBox>

      <FadeInBox
        sx={{
          display: 'flex',
          flexDirection: 'column',
          my: 6,
          p: 12,
          backgroundColor: isDarkMode ? grey[900] : green[50],
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography sx={{ fontWeight: 'bold' }} variant='h4'>
            Your Locustfile. Our Cloud.
          </Typography>
          <Typography variant='subtitle1'>
            Running locust cloud couldn't be easier. Simply upload your locustfile and you're off to
            the races.
          </Typography>
        </Box>

        <Box>
          <img src='/assets/terminal.gif' width='100%' />
        </Box>
      </FadeInBox>

      <FadeInBox
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          alignItems: 'center',
          my: 12,
        }}
      >
        <Box sx={{ px: 8 }}>
          <Typography variant='h4'>Dive Deeper</Typography>
          <Typography variant='subtitle1'>
            With locust cloud you can get more out of each testrun. Get a detailed view into
            individual requests and identify bottlenecks with ease.
          </Typography>
        </Box>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Box>
            {isDarkMode ? (
              <img src='/assets/graphs-dark.png' width='100%' />
            ) : (
              <img src='/assets/graphs-light.png' width='100%' />
            )}
          </Box>
        </Box>
      </FadeInBox>

      <FadeInBox
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          alignItems: 'center',
          my: 12,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Box>
            {isDarkMode ? (
              <img src='/assets/testruns-dark.png' width='100%' />
            ) : (
              <img src='/assets/testruns-light.png' width='100%' />
            )}
          </Box>
        </Box>
        <Box sx={{ px: 8 }}>
          <Typography variant='h4'>See Everything</Typography>
          <Typography variant='subtitle1'>
            Every locust testrun is saved. Keep track of how your system has performed historically
            and get notified immediately when performace degrades
          </Typography>
        </Box>
      </FadeInBox>

      <FadeInBox>
        <Typography sx={{ textAlign: 'center', mb: 6 }} variant='h4'>
          Pricing Plans to Fit your Needs
        </Typography>
        <Pricing />
      </FadeInBox>
    </Box>
  );
}
