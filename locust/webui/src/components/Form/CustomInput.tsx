import { Checkbox, FormControlLabel, TextField } from '@mui/material';

import PasswordField from 'components/Form/PasswordField';
import Select from 'components/Form/Select';
import { ICustomInput } from 'types/form.types';

export default function CustomInput({
  name,
  label,
  type = 'text',
  defaultValue,
  choices,
  isSecret,
  isRequired,
}: ICustomInput) {
  if (choices) {
    return (
      <Select
        defaultValue={defaultValue as string}
        label={label}
        name={name}
        options={choices}
        required={isRequired}
        sx={{ width: '100%' }}
      />
    );
  }

  if (typeof defaultValue === 'boolean') {
    return (
      <FormControlLabel
        control={<Checkbox defaultChecked={defaultValue} required={isRequired} />}
        label={label}
        name={name}
      />
    );
  }

  if (isSecret) {
    return (
      <PasswordField
        defaultValue={defaultValue}
        isRequired={isRequired}
        label={label}
        name={name}
      />
    );
  }

  return (
    <TextField
      defaultValue={defaultValue}
      label={label}
      name={name}
      required={isRequired}
      sx={{ width: '100%' }}
      type={type}
    />
  );
}
