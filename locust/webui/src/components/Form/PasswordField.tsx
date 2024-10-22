import { useState } from 'react';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { FormControl, IconButton, InputAdornment, InputLabel, OutlinedInput } from '@mui/material';

import { ICustomInput } from 'types/form.types';

export default function PasswordField({
  name = 'password',
  label = 'Password',
  defaultValue,
}: Pick<ICustomInput, 'name' | 'label' | 'defaultValue'>) {
  const [showPassword, setShowPassword] = useState(false);

  const handleClickShowPassword = () => setShowPassword(!showPassword);

  return (
    <FormControl variant='outlined'>
      <InputLabel htmlFor={`${label}-${name}-field`}>{label}</InputLabel>
      <OutlinedInput
        defaultValue={defaultValue}
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
