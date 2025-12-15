import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CreditCardOffIcon from '@mui/icons-material/CreditCardOff';
import GroupsIcon from '@mui/icons-material/Groups';
import PersonIcon from '@mui/icons-material/Person';
import SpeedIcon from '@mui/icons-material/Speed';
import SupportIcon from '@mui/icons-material/Support';
import { Box } from '@mui/material';

import PricingCard from 'components/LocustCloudTab/PricingCard';

const freeFeatures = [
  {
    icon: <AccessTimeIcon />,
    title: '200 VUh per month',
    description: '',
  },
  {
    icon: <PersonIcon />,
    title: 'Up to 100 Virtual Users',
    description: '',
  },
  {
    icon: <SpeedIcon />,
    title: 'Distributed Tests',
    description: 'Get access to up to 2 workers',
  },
  {
    icon: <CreditCardOffIcon />,
    title: 'No Credit Card Required, no Trial Clock',
    description: 'Free load testing, no strings attached!',
  },
  {},
];

const premiumFeatures = [
  {
    icon: <AccessTimeIcon />,
    title: '5,000 VUh per month',
    description: 'Enough capacity to run bigger tests, or smaller tests several times per month',
  },
  {
    icon: <PersonIcon />,
    title: 'Up to 1,000 Virtual Users',
    description: 'Simulate real world load with more virtual users',
  },
  {
    icon: <SpeedIcon />,
    title: 'Distributed Tests',
    description: 'Get access to up to 4 workers',
  },
  {
    icon: <GroupsIcon />,
    title: 'Teams',
    description: 'Up to 5 users',
  },
  {
    icon: <SupportIcon />,
    title: 'Priority Support',
    description: 'Get help faster with dedicated support channels',
  },
];

const unlimitedFeatures = [
  {
    icon: <AccessTimeIcon />,
    title: 'Up to 5 million VUh per month',
    description: 'Any capacity you need, we can provide',
  },
  {
    icon: <PersonIcon />,
    title: 'Up to 1 million Virtual Users',
    description: 'Prepare your system to handle load of any size',
  },
  {
    icon: <SpeedIcon />,
    title: 'Distributed Tests',
    description: 'No limits on the number of workers',
  },
  {
    icon: <GroupsIcon />,
    title: 'Teams',
    description: 'Unlimited users',
  },
  {
    icon: <SupportIcon />,
    title: 'Priority Support',
    description:
      'Get help faster and receive consultation hours for building your locust test scripts',
  },
];

export default function Pricing() {
  return (
    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4, m: 6 }}>
      <PricingCard
        ctaText='Join for Free'
        features={freeFeatures}
        href='https://app.locust.cloud/signup'
        price='$0'
        tierName='Free'
      />
      <PricingCard
        ctaText='Get Started'
        features={premiumFeatures}
        href='https://app.locust.cloud/signup?plan=premium'
        price='$399'
        recommended
        tierName='Premium'
      />
      <PricingCard
        ctaText='Request a consultation'
        features={unlimitedFeatures}
        href='https://www.locust.cloud/get-started?plan=unlimited'
        tierName='Unlimited'
      />
    </Box>
  );
}
