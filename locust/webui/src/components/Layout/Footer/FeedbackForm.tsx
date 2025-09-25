import { useState } from 'react';
import { Alert, Box, Button, TextField, Typography } from '@mui/material';

import Form from 'components/Form/Form';
import Modal from 'components/Modal/Modal';
import LoadingButton from 'components/SwarmForm/LoadingButton';

interface IFeedbackForm {
  email: string;
  message: string;
}

const unexpectedErrorMessage =
  "We're sorry but something seems to have gone wrong. Please try again or reach out to us directly at support@locust.cloud";

export default function FeedbackForm() {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [success, setSuccess] = useState<boolean>();

  const onSubmitFeedback = async (inputData: IFeedbackForm) => {
    setIsLoading(true);

    try {
      const response = await fetch('https://api.locust.cloud/1/customer/send-feedback', {
        method: 'POST',
        body: JSON.stringify(inputData),
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.status >= 400) {
        setErrorMessage(unexpectedErrorMessage);
      } else {
        setSuccess(true);
      }
    } catch {
      setErrorMessage(unexpectedErrorMessage);
    }

    setIsLoading(false);
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button color='inherit' onClick={() => setOpen(true)} variant='text'>
          Feedback
        </Button>
      </Box>
      <Modal onClose={() => setOpen(false)} open={open}>
        {success ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              textAlign: 'center',
              height: 200,
            }}
          >
            <Typography component='h4' sx={{ mb: 2 }} variant='h4'>
              Thanks for reaching out!
            </Typography>
            <Typography component='h4' variant='h5'>
              Your feedback is very valuable to us as we work to improve Locust!
            </Typography>
          </Box>
        ) : (
          <Form<IFeedbackForm> onSubmit={onSubmitFeedback}>
            <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 2, my: 2 }}>
              <TextField label='Email' name='email' required type='email' />
              <TextField label='Name' name='name' />
              <TextField label='Message' multiline name='message' required rows={3} />
              {!!errorMessage && <Alert severity='error'>{errorMessage}</Alert>}

              <LoadingButton isLoading={isLoading} type='submit'>
                Submit
              </LoadingButton>
            </Box>
          </Form>
        )}
      </Modal>
    </>
  );
}
