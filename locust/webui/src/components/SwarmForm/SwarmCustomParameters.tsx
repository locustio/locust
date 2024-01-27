import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Checkbox,
  FormControlLabel,
  TextField,
  Typography,
} from '@mui/material';

import Select from 'components/Form/Select';
import { IExtraOptionParameter, IExtraOptions } from 'types/swarm.types';
import { toTitleCase } from 'utils/string';

interface ICustomParameters {
  extraOptions: IExtraOptions;
}

interface ICustomInputProps extends IExtraOptionParameter {
  label: string;
}

function CustomInput({ label, defaultValue, choices, helpText, isSecret }: ICustomInputProps) {
  const labelTitle = toTitleCase(label);
  const labelWithOptionalHelpText = helpText ? `${labelTitle} (${helpText})` : labelTitle;

  if (choices) {
    return (
      <Select
        defaultValue={defaultValue as string}
        label={labelWithOptionalHelpText}
        name={label}
        options={choices}
        sx={{ width: '100%' }}
      />
    );
  }

  if (typeof defaultValue === 'boolean') {
    return (
      <FormControlLabel
        control={<Checkbox defaultChecked={defaultValue} />}
        label={labelWithOptionalHelpText}
        name={label}
      />
    );
  }

  return (
    <TextField
      defaultValue={defaultValue}
      label={labelWithOptionalHelpText}
      name={label}
      sx={{ width: '100%' }}
      type={isSecret ? 'password' : 'text'}
    />
  );
}

export default function CustomParameters({ extraOptions }: ICustomParameters) {
  return (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography>Custom parameters</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4 }}>
          {Object.entries(extraOptions).map(([label, inputProps], index) => (
            <CustomInput key={`valid-parameter-${index}`} label={label} {...inputProps} />
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}
