import { Alert, Box, Button, IconButton, TextField, Typography } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';

import Logo from 'assets/Logo';
import DarkLightToggle from 'components/Layout/Navbar/DarkLightToggle';
import useCreateTheme from 'hooks/useCreateTheme';
import { IAuthArgs } from 'types/auth.types';

export default function Auth({ authProviders, error, usernamePasswordCallback }: IAuthArgs) {
  const theme = useCreateTheme();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <Box sx={{ position: 'absolute', top: 4, right: 4 }}>
        <DarkLightToggle />
      </Box>
      <Box
        component='main'
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          display: 'flex',
          flexDirection: 'column',
          rowGap: 4,
          boxShadow: 24,
          borderRadius: 4,
          border: '3px solid black',
          p: 4,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'center', columnGap: 2 }}>
          <Logo lightModeBackgroundColor='#fff' />
        </Box>
        {usernamePasswordCallback && (
          <form action={usernamePasswordCallback}>
            <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 2 }}>
              <TextField label='Username' name='username' />
              <TextField label='Password' name='password' type='password' />
              {error && <Alert severity='error'>{error}</Alert>}
              <Button size='large' type='submit' variant='contained'>
                Login
              </Button>
            </Box>
          </form>
        )}
        {authProviders && (
          <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 1 }}>
            {authProviders.map(({ label, callbackUrl, iconUrl }, index) => (
              <IconButton
                href={callbackUrl}
                key={`auth-provider-${index}`}
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  columnGap: 2,
                  borderRadius: 2,
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'primary',
                }}
              >
                <img height='32' src={iconUrl} />
                <Typography height='32' variant='button'>
                  {label}
                </Typography>
              </IconButton>
            ))}
          </Box>
        )}
      </Box>
    </ThemeProvider>
  );
}
