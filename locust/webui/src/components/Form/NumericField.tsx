import { useEffect, useState } from 'react';
import { TextField, TextFieldProps } from '@mui/material';

export default function NumericField({ defaultValue, ...textFieldProps }: TextFieldProps) {
  const [value, setValue] = useState<string>((defaultValue as string) || '');

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

  useEffect(() => {
    if (defaultValue) {
      setValue(defaultValue as string);
    }
  }, [defaultValue]);

  return <TextField {...textFieldProps} onChange={filterNonNumeric} value={value} />;
}
