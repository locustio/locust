import { useMemo } from 'react';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
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
  defaultValue: string;
}

const isParamterValid = (parameter: IExtraOptionParameter) =>
  parameter.defaultValue !== null && typeof parameter.defaultValue !== 'boolean';

function CustomInput({ label, defaultValue, choices, helpText, isSecret }: ICustomInputProps) {
  const labelTitle = toTitleCase(label);
  const labelWithOptionalHelpText = helpText ? `${labelTitle} (${helpText})` : labelTitle;

  if (choices) {
    return (
      <Select
        defaultValue={defaultValue}
        label={labelWithOptionalHelpText}
        name={label}
        options={choices}
        sx={{ width: '100%' }}
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
  const validParameters = useMemo<ICustomInputProps[]>(
    () =>
      Object.entries(extraOptions).reduce(
        (filteredParamaters: ICustomInputProps[], [key, value]) =>
          isParamterValid(value)
            ? ([...filteredParamaters, { label: key, ...value }] as ICustomInputProps[])
            : filteredParamaters,
        [],
      ),
    [extraOptions],
  );
  const invalidParameters = useMemo<string[]>(
    () =>
      Object.keys(extraOptions).reduce(
        (filteredParamaters: string[], key) =>
          isParamterValid(extraOptions[key]) ? filteredParamaters : [...filteredParamaters, key],
        [],
      ),
    [extraOptions],
  );

  return (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography>Custom parameters</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 4 }}>
          {validParameters.map((parameter, index) => (
            <CustomInput key={`valid-parameter-${index}`} {...parameter} />
          ))}
          <Box>
            {invalidParameters && (
              <>
                <Typography>
                  The following custom parameters can't be set in the Web UI, because it is a
                  boolean or None type:
                </Typography>
                <ul>
                  {invalidParameters.map((parameter, index) => (
                    <li key={`invalid-parameter-${index}`}>
                      <Typography>{parameter}</Typography>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </Box>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}
