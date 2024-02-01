import { SxProps, FormControl, InputLabel, Select as MuiSelect, SelectProps } from '@mui/material';

interface ISelect extends SelectProps {
  label: string;
  name: string;
  options: string[];
  multiple?: boolean;
  defaultValue?: string | string[];
  sx?: SxProps;
}

export default function Select({
  label,
  name,
  options,
  multiple = false,
  defaultValue,
  sx,
}: ISelect) {
  return (
    <FormControl sx={sx}>
      <InputLabel htmlFor={name} shrink>
        {label}
      </InputLabel>
      <MuiSelect
        defaultValue={defaultValue || (multiple && options) || options[0]}
        id={name}
        label={label}
        multiple={multiple}
        name={name}
        native
      >
        {options.map((option, index) => (
          <option key={`option-${option}-${index}`} value={option}>
            {option}
          </option>
        ))}
      </MuiSelect>
    </FormControl>
  );
}
