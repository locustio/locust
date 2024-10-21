import { useState } from 'react';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { FormControl, IconButton, InputAdornment, InputLabel, OutlinedInput } from '@mui/material';

export default function PasswordField({ name = 'password', label = 'Password' }) {
  const [showPassword, setShowPassword] = useState(false);

  const handleClickShowPassword = () => setShowPassword(!showPassword);

  return (
    <FormControl variant='outlined'>
      <InputLabel htmlFor='password-field'>{label}</InputLabel>
      <OutlinedInput
        endAdornment={
          <InputAdornment position='end'>
            <IconButton edge='end' onClick={handleClickShowPassword}>
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </IconButton>
          </InputAdornment>
        }
        id={`${label}-${name}-field`}
        label={label}
        name={name}
        type={showPassword ? 'text' : 'password'}
      />
    </FormControl>
  );
}
