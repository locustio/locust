import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Accordion, AccordionDetails, AccordionSummary, Box, Typography } from '@mui/material';

import CustomInput from 'components/Form/CustomInput';
import { IExtraOptions } from 'types/swarm.types';
import { toTitleCase } from 'utils/string';

interface ICustomParameters {
  extraOptions: IExtraOptions;
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
            <CustomInput
              {...inputProps}
              key={`valid-parameter-${index}`}
              label={
                inputProps.helpText
                  ? `${toTitleCase(label)} (${inputProps.helpText})`
                  : toTitleCase(label)
              }
              name={label}
            />
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}
