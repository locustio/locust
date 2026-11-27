import { useEffect, useState } from 'react';
import { Alert, Box, Button, CircularProgress, Typography } from '@mui/material';

import ConfigEditor from 'components/DynamicConfig/ConfigEditor';
import { useGetDynamicConfigQuery, useUpdateDynamicConfigMutation } from 'redux/api/swarm';
import { IDynamicConfig } from 'types/dynamicConfig.types';

const getErrorMessage = (error: unknown) =>
  (error as { data?: { message?: string } } | undefined)?.data?.message ||
  'Failed to update dynamic config';

export default function DynamicConfig() {
  const { data: config } = useGetDynamicConfigQuery(undefined, { refetchOnMountOrArgChange: true });
  const [updateDynamicConfig, { isLoading, isSuccess, isError, data, error }] =
    useUpdateDynamicConfigMutation();
  const [draft, setDraft] = useState<IDynamicConfig>({});

  useEffect(() => {
    if (config) {
      setDraft(config);
    }
  }, [config]);

  return (
    <Box sx={{ maxWidth: 800 }}>
      <Typography component='p' sx={{ mb: 3 }} variant='body2'>
        Settings that can be changed while the test is running. Changes apply to all workers.
      </Typography>
      {Object.entries(draft).map(([userClass, userClassConfig]) => (
        <Box key={userClass} sx={{ mb: 3 }}>
          <Typography component='h2' sx={{ mb: 2 }} variant='h6'>
            {userClass}
          </Typography>
          <ConfigEditor
            config={userClassConfig}
            onChange={nextConfig => setDraft({ ...draft, [userClass]: nextConfig })}
          />
        </Box>
      ))}
      <Box sx={{ alignItems: 'center', display: 'flex', gap: 2 }}>
        <Button disabled={isLoading} onClick={() => updateDynamicConfig(draft)} variant='contained'>
          Update Config
          {isLoading && <CircularProgress size={20} sx={{ ml: 2 }} />}
        </Button>
        {isSuccess && <Alert severity='success'>{data?.message}</Alert>}
        {isError && <Alert severity='error'>{getErrorMessage(error)}</Alert>}
      </Box>
    </Box>
  );
}
