import { Checkbox, FormControlLabel, TextField } from '@mui/material';

import PasswordField from 'components/Form/PasswordField';
import Select from 'components/Form/Select';
import { ICustomInput } from 'types/form.types';

export default function CustomInput({
  name,
  label,
  defaultValue,
  choices,
  isSecret,
}: ICustomInput) {
  if (choices) {
    return (
      <Select
        defaultValue={defaultValue as string}
        label={label}
        name={name}
        options={choices}
        sx={{ width: '100%' }}
      />
    );
  }

  if (typeof defaultValue === 'boolean') {
    return (
      <FormControlLabel
        control={<Checkbox defaultChecked={defaultValue} />}
        label={label}
        name={name}
      />
    );
  }

  if (isSecret) {
    return <PasswordField label={label} name={name} />;
  }

  return (
    <TextField
      defaultValue={defaultValue}
      label={label}
      name={name}
      sx={{ width: '100%' }}
      type='text'
    />
  );
}
