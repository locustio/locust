import { useEffect, useState } from 'react';
import { Box, FormControlLabel, Stack, Switch, TextField, Typography } from '@mui/material';

import { JsonObject, JsonValue } from 'types/dynamicConfig.types';

interface IConfigEditor {
  config: JsonObject;
  onChange: (config: JsonObject) => void;
}

interface IConfigField {
  label: string;
  value: JsonValue;
  onChange: (value: JsonValue) => void;
}

const isObject = (value: JsonValue): value is JsonObject =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const kindOf = (value: JsonValue) =>
  value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;

const parseJson = (text: string): { value?: JsonValue; isValid: boolean } => {
  try {
    return { value: JSON.parse(text), isValid: true };
  } catch {
    return { isValid: false };
  }
};

// Edits numbers, arrays and null as JSON text. Only text that parses to the same kind of value is
// committed, so a setting can't silently change type while it is being typed.
function JsonTextField({ label, value, onChange }: IConfigField) {
  const [text, setText] = useState(JSON.stringify(value));
  const [isInvalid, setIsInvalid] = useState(false);

  useEffect(() => {
    const { value: parsed, isValid } = parseJson(text);
    if (!isValid || JSON.stringify(parsed) !== JSON.stringify(value)) {
      setText(JSON.stringify(value));
      setIsInvalid(false);
    }
  }, [value]);

  const onTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextText = event.target.value;
    const { value: parsed, isValid } = parseJson(nextText);
    const isAccepted = isValid && (value === null || kindOf(parsed as JsonValue) === kindOf(value));

    setText(nextText);
    setIsInvalid(!isAccepted);
    if (isAccepted) {
      onChange(parsed as JsonValue);
    }
  };

  return (
    <TextField
      error={isInvalid}
      fullWidth
      helperText={isInvalid ? `Enter a valid JSON ${kindOf(value)}` : undefined}
      label={label}
      onChange={onTextChange}
      size='small'
      value={text}
    />
  );
}

function ConfigField({ label, value, onChange }: IConfigField) {
  if (isObject(value)) {
    return (
      <Box>
        <Typography sx={{ fontWeight: 'bold' }} variant='body2'>
          {label}
        </Typography>
        <Box sx={{ borderLeft: 2, borderColor: 'divider', mt: 1, pl: 2 }}>
          <ConfigEditor config={value} onChange={onChange} />
        </Box>
      </Box>
    );
  }

  if (typeof value === 'boolean') {
    return (
      <FormControlLabel
        control={
          <Switch checked={value} onChange={event => onChange(event.target.checked)} size='small' />
        }
        label={label}
      />
    );
  }

  if (typeof value === 'string') {
    return (
      <TextField
        fullWidth
        label={label}
        onChange={event => onChange(event.target.value)}
        size='small'
        value={value}
      />
    );
  }

  return <JsonTextField label={label} onChange={onChange} value={value} />;
}

export default function ConfigEditor({ config, onChange }: IConfigEditor) {
  return (
    <Stack spacing={2}>
      {Object.entries(config).map(([key, value]) => (
        <ConfigField
          key={key}
          label={key}
          onChange={nextValue => onChange({ ...config, [key]: nextValue })}
          value={value}
        />
      ))}
    </Stack>
  );
}
