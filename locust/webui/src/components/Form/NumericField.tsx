import { useState } from 'react';
import { TextField, TextFieldProps } from '@mui/material';

export default function NumericField(textFieldProps: TextFieldProps) {
  const [value, setValue] = useState<string>((textFieldProps.defaultValue as string) || '');

  const filterNonNumeric = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (textFieldProps.onChange) {
      textFieldProps.onChange(event);
    }

    const currentValue = event.target.value;
    const decimalPoints = (currentValue.match(/\./g) || []).length;

    if (decimalPoints > 1) {
      return;
    }

    setValue(event.target.value.replace(/[^0-9.]/g, ''));
  };

  return <TextField {...textFieldProps} onInput={filterNonNumeric} value={value} />;
}
