import {
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Button,
} from '@mui/material';

interface IPricingCard {
  tierName: string;
  price?: string;
  features: any[];
  recommended?: boolean;
  ctaText: string;
  onClick?: () => void;
  href?: string;
  isLoading?: boolean;
}

export default function PricingCard({
  tierName,
  price,
  features,
  recommended,
  ctaText,
  href,
}: IPricingCard) {
  return (
    <Card
      sx={{
        flex: 1,
        border: recommended ? 2 : undefined,
        borderColor: recommended ? 'primary.main' : undefined,
        position: 'relative',
        overflow: 'visible',
      }}
    >
      {recommended && (
        <Box
          sx={{
            position: 'absolute',
            top: -12,
            left: 24,
            bgcolor: 'primary.main',
            color: 'white',
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontSize: '0.875rem',
            fontWeight: 'bold',
          }}
        >
          Recommended
        </Box>
      )}
      <CardContent sx={{ p: 4, pt: 5 }}>
        <Box sx={{ height: { md: '120px' } }}>
          <Typography component='h2' sx={{ fontWeight: 'bold', mb: 2 }} variant='h5'>
            {tierName}
          </Typography>
          {price && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'baseline',
                gap: 0.5,
                mb: 2,
              }}
            >
              <Typography sx={{ fontWeight: 'bold' }} variant='h4'>
                {price}
              </Typography>
              <Typography color='text.secondary' variant='body1'>
                /month
              </Typography>
            </Box>
          )}
        </Box>

        <List sx={{ mb: 4 }}>
          {features.map(({ title, description, icon }, index) => (
            <ListItem key={`pricing-${title}-${index}`} sx={{ height: 74 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>{icon}</ListItemIcon>
              <ListItemText
                primary={
                  <Typography sx={{ fontWeight: 'medium' }} variant='body1'>
                    {title}
                  </Typography>
                }
                secondary={description}
              />
            </ListItem>
          ))}
        </List>

        {recommended ? (
          <Button
            href={href}
            size='large'
            sx={{
              width: '100%',
              mt: 'auto',
              px: 4,
              py: 1.5,
              textTransform: 'none',
              backgroundImage: 'linear-gradient(to right, #15803d, oklch(62.7% 0.194 149.214))',
            }}
            variant='contained'
          >
            {ctaText}
          </Button>
        ) : (
          <Button
            href={href}
            size='large'
            sx={{
              width: '100%',
              mt: 'auto',
              px: 4,
              py: 1.5,
              textTransform: 'none',
              color: theme => theme.palette.text.primary,
              border: theme => `1px solid ${theme.palette.text.primary}`,
            }}
            variant='outlined'
          >
            {ctaText}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
