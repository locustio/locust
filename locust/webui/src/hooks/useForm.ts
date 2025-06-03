import { ChangeEvent, useState } from 'react';
import { AlertColor, Theme } from '@mui/material';

type MatchRule = {
  pattern: RegExp;
  message?: string;
};

type ValidationRules = {
  minLength?: number;
  match?: MatchRule | MatchRule[];
  level?: AlertColor;
};

type Errors = Record<string, string>;

export default function useForm() {
  const [errors, setErrors] = useState<Errors>({});
  const [isValid, setIsValid] = useState<boolean>(true);

  const validate = (
    name: string,
    value: string,
    rules: ValidationRules,
    { onlyDelete } = { onlyDelete: false },
  ) => {
    const newErrors = { ...errors };
    let errorMessage;
    const failedMatch =
      rules.match &&
      Array.isArray(rules.match) &&
      rules.match.find(({ pattern }) => !new RegExp(pattern).test(value));

    if (rules.minLength && value.length < rules.minLength) {
      errorMessage = `Please enter at least ${rules.minLength} characters`;
    } else if (failedMatch) {
      errorMessage = failedMatch.message || 'Invalid format';
    } else if (
      rules.match &&
      !Array.isArray(rules.match) &&
      !new RegExp(rules.match.pattern).test(value)
    ) {
      errorMessage = rules.match.message || 'Invalid format';
    } else {
      delete newErrors[name];
    }

    if (errorMessage && !onlyDelete) {
      newErrors[name] = errorMessage;
    }

    setErrors(newErrors);
    setIsValid(Object.keys(newErrors).length === 0);
  };

  const register = (name: string, rules: ValidationRules, mode = 'onChange') => {
    const alertLevelProps =
      errors[name] && rules.level
        ? {
            color: rules.level,
            focused: true,
            FormHelperTextProps: {
              sx: { color: (theme: Theme) => theme.palette.warning.main },
            },
          }
        : {};

    return {
      ...alertLevelProps,
      name,
      onChange: ({ target: { value } }: ChangeEvent<HTMLInputElement>) =>
        validate(name, value, rules, { onlyDelete: true }),
      [mode]: ({ target: { value } }: ChangeEvent<HTMLInputElement>) =>
        validate(name, value, rules),
      error: !!errors[name] && !rules.level,
      helperText: errors[name] || '',
    };
  };

  return { register, isValid };
}
