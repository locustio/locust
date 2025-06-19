import { useEffect } from 'react';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import SpeedIcon from '@mui/icons-material/Speed';
import SupportIcon from '@mui/icons-material/Support';
import { Box } from '@mui/material';

import useUpgradeToPaid from 'hooks/useUpgradeToPaid';
import { useAction } from 'redux/hooks';
import { snackbarActions } from 'redux/slice/snackbar.slice';

import PricingCard from './PricingCard';

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
    description: 'Get access to up to 100 workers',
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
    icon: <SupportIcon />,
    title: 'Priority Support',
    description:
      'Get help faster and receive consultation hours for building your locust test scripts',
  },
];

export default function UpgradePrompt() {
  const { onUpgradeTier, isLoading, error: upgradeTierError } = useUpgradeToPaid();
  const setSnackbar = useAction(snackbarActions.setSnackbar);

  useEffect(() => {
    if (upgradeTierError) {
      setSnackbar({
        message:
          'An unexpected error has occured. Please try again or contact support@locust.cloud.',
        severity: 'error',
      });
    }
  }, [upgradeTierError]);

  return (
    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
      <PricingCard
        ctaText='Upgrade Now'
        features={premiumFeatures}
        isLoading={isLoading}
        onClick={onUpgradeTier}
        price='$399'
        recommended
        tierName='Unlock Premium Features'
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
