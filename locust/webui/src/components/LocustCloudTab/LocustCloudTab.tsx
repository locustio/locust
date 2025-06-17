import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BoltIcon from '@mui/icons-material/Bolt';
import CheckIcon from '@mui/icons-material/Check';
import PersonIcon from '@mui/icons-material/Person';
import ShieldIcon from '@mui/icons-material/Shield';
import { Box, Button, Card, Paper, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';

import { useSelector } from 'redux/hooks';

export default function LocustCloudTab() {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

  return (
    <Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', rowGap: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            columnGap: 1,
            rowGap: 4,
            mt: 6,
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
              px: 4,
              py: 2,
              borderRadius: 2,
              backgroundColor: 'rgb(22, 163, 74)',
            }}
            variant='contained'
          >
            Start Free Trial
          </Button>
          <Button
            sx={{
              textTransform: 'none',
              px: 4,
              py: 2,
              borderRadius: 2,
              color: 'black',
              borderColor: 'black',
            }}
            variant='outlined'
          >
            Request a Consultation
          </Button>
        </Box>
        <Box
          sx={{
            display: 'grid',
            columnGap: 12,
            gridTemplateColumns: 'repeat(2, 1fr)',
            alignItems: 'center',
            my: 12,
          }}
        >
          <Box sx={{ px: 8 }}>
            <Typography variant='h4'>Your Locustfile. Our Cloud.</Typography>
            <Typography variant='subtitle1'>
              Running locust cloud couldn't be easier. Simply upload your locustfile and you're off
              to the races.
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
              <img src='/assets/locust-terminal-screenshot.png' width='400px' />
            </Box>
            <ArrowForwardIcon height='40px' sx={{ mt: 1, mb: 2 }} width='40px' />
            <Box>
              <img src='/assets/locust-cloud-terminal-screenshot.png' width='400px' />
            </Box>
          </Box>
        </Box>

        <Box
          sx={{
            display: 'grid',
            columnGap: 12,
            gridTemplateColumns: '1fr 0.6fr',
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
                <img src='/assets/graphs-dark.png' width='100%' />
              ) : (
                <img src='/assets/graphs-light.png' width='100%' />
              )}
            </Box>
          </Box>
          <Box sx={{ px: 8 }}>
            <Typography variant='h4'>Dive Deeper</Typography>
            <Typography variant='subtitle1'>
              With locust cloud you can get more out of each testrun. Get a detailed view into
              individual requests and identify bottlenecks with ease.
            </Typography>
          </Box>
        </Box>

        <Box
          sx={{
            display: 'grid',
            columnGap: 12,
            gridTemplateColumns: '0.6fr 1fr',
            alignItems: 'center',
            my: 12,
          }}
        >
          <Box sx={{ px: 8 }}>
            <Typography variant='h4'>See Everything</Typography>
            <Typography variant='subtitle1'>
              Every locust testrun is saved. Keep track of how your system has performed
              historically and get notified immediately when performace degrades
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
                <img src='/assets/testruns-dark.png' width='100%' />
              ) : (
                <img src='/assets/testruns-light.png' width='100%' />
              )}
            </Box>
          </Box>
        </Box>
      </Box>

      <Box sx={{ py: 8, px: 8, my: 12, backgroundColor: 'oklch(98.4% 0.003 247.858)' }}>
        <Typography sx={{ fontWeight: 'bold', textAlign: 'center' }} variant='h4'>
          Our Features
        </Typography>
        <Typography
          sx={{ color: isDarkMode ? '#fff' : grey[700], textAlign: 'center' }}
          variant='h6'
        >
          Discover what sets Locust Cloud apart
        </Typography>
        <Box
          sx={{
            mt: 4,
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 4,
          }}
        >
          <Card
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '40px',
                width: '40px',
                backgroundColor: 'oklch(94.6% 0.033 307.174)',
                borderRadius: '100%',
                mb: 2,
              }}
            >
              <BoltIcon
                stroke='oklch(55.8% 0.288 302.321)'
                sx={{ fill: 'none', height: '30px', width: '30px' }}
              />
            </Box>
            <Typography sx={{ fontWeight: 'bold', mb: 1 }} variant='h6'>
              Lightning Fast
            </Typography>
            <Typography sx={{ textAlign: 'center', color: isDarkMode ? '#fff' : grey[700] }}>
              Your distributed load tests will be ready to run in seconds
            </Typography>
          </Card>
          <Card
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '40px',
                width: '40px',
                backgroundColor: 'oklch(96.2% 0.044 156.743)',
                borderRadius: '100%',
                mb: 2,
              }}
            >
              <ShieldIcon
                stroke='oklch(62.7% 0.194 149.214)'
                sx={{ fill: 'none', height: '30px', width: '30px' }}
              />
            </Box>
            <Typography sx={{ fontWeight: 'bold', mb: 1 }} variant='h6'>
              Advanced Security
            </Typography>
            <Typography sx={{ textAlign: 'center', color: isDarkMode ? '#fff' : grey[700] }}>
              Military grade encryption ISO/IEC 27001 SOC NIST HIPAA compliant stored on Mars
            </Typography>
          </Card>
          <Card
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '40px',
                width: '40px',
                backgroundColor: 'oklch(95.1% 0.026 236.824)',
                borderRadius: '100%',
                mb: 2,
              }}
            >
              <AccessTimeIcon
                stroke='oklch(58.8% 0.158 241.966)'
                sx={{ fill: 'none', height: '30px', width: '30px' }}
              />
            </Box>
            <Typography sx={{ fontWeight: 'bold', mb: 1 }} variant='h6'>
              Scheduled Testing
            </Typography>
            <Typography sx={{ textAlign: 'center', color: isDarkMode ? '#fff' : grey[700] }}>
              Automate your load tests with scheduled CI/CD integration
            </Typography>
          </Card>
        </Box>
      </Box>

      <Typography sx={{ textAlign: 'center' }} variant='h4'>
        Competitve Pricing? You Bet!
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', columnGap: 4, mt: 6, mb: 6 }}>
        <Paper sx={{ width: '400px', p: 2 }}>
          <Typography variant='h6'>Free Tier</Typography>
          <Box sx={{ display: 'flex', columnGap: 0.1, alignItems: 'flex-end', height: '30px' }}>
            <Typography sx={{ fontWeight: 'bold' }} variant='h6'>
              $0
            </Typography>
            <Typography color={grey[700]} variant='subtitle1'>
              /month
            </Typography>
          </Box>
          <Box sx={{ my: 2 }}>
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1, my: 0.5 }}>
                <AccessTimeIcon />
                <Typography sx={{ marginBottom: '-5px' }}>200 VUh</Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
                <PersonIcon />
                <Typography sx={{ marginBottom: '-5px' }}>100 VU</Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Advanced graphs</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Stored testruns</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Distributed tests with 2 workers</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography sx={{ fontWeight: 'bold' }} variant='subtitle1'>
                No credit card required, no trial clock
              </Typography>
            </Box>
          </Box>
          <Button sx={{ width: '100%', textTransform: 'none', color: 'black' }} variant='outlined'>
            Join for Free
          </Button>
        </Paper>
        <Paper sx={{ width: '400px', p: 2 }}>
          <Typography variant='h6'>Premium Tier</Typography>
          <Box sx={{ display: 'flex', columnGap: 0.1, alignItems: 'flex-end', height: '30px' }}>
            <Typography sx={{ fontWeight: 'bold' }} variant='h6'>
              $399
            </Typography>
            <Typography color={grey[700]} variant='subtitle1'>
              /month
            </Typography>
          </Box>
          <Box sx={{ my: 2 }}>
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1, my: 0.5 }}>
                <AccessTimeIcon />
                <Typography sx={{ marginBottom: '-5px' }}>5000 VUh</Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
                <PersonIcon />
                <Typography sx={{ marginBottom: '-5px' }}>1000 VU</Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Advanced graphs</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Stored testruns</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Distributed tests with 1-100 workers</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Professional consultation and support</Typography>
            </Box>
          </Box>
          <Button
            sx={{
              width: '100%',
              textTransform: 'none',
              backgroundImage: 'linear-gradient(to right, #15803d, oklch(62.7% 0.194 149.214))',
            }}
            variant='contained'
          >
            Try Premium for Free
          </Button>
        </Paper>
        <Paper sx={{ width: '400px', p: 2 }}>
          <Typography variant='h6'>Unlimited</Typography>
          <Box sx={{ height: '30px' }} />

          <Box sx={{ my: 2 }}>
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1, my: 0.5 }}>
                <AccessTimeIcon />
                <Typography sx={{ marginBottom: '-5px' }}>Up to 5M VUh</Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
                <PersonIcon />
                <Typography sx={{ marginBottom: '-5px' }}>Up to 1M VU</Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Advanced graphs</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Stored testruns</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Distributed test with unlimited workers</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', columnGap: 1 }}>
              <CheckIcon color='success' />
              <Typography variant='subtitle1'>Professional consultation and support</Typography>
            </Box>
          </Box>
          <Button
            sx={{
              width: '100%',
              mt: 'auto',
              textTransform: 'none',
              backgroundImage: 'linear-gradient(to right, #15803d, oklch(62.7% 0.194 149.214))',
            }}
            variant='contained'
          >
            Request a consultation
          </Button>
        </Paper>
      </Box>
    </Box>
  );
}
