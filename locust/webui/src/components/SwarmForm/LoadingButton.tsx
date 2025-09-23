import { Button, ButtonProps, CircularProgress } from '@mui/material';

interface ILoadingButton extends ButtonProps {
  isLoading?: boolean;
  children?: React.ReactNode;
}

export default function LoadingButton({ isLoading, children, variant, ...props }: ILoadingButton) {
  return (
    <>
      <Button
        {...props}
        disabled={props.disabled || isLoading}
        size='large'
        sx={{ ...props.sx, textTransform: 'none' }}
        variant={variant || 'contained'}
      >
        {isLoading ? <CircularProgress size={25} sx={{ color: 'white' }} /> : children || 'Submit'}
      </Button>
    </>
  );
}
