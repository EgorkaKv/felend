import { default as MuiButton } from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import type { ButtonProps as MuiButtonProps } from '@mui/material/Button';

interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'primary' | 'outlined' | 'text';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = ({
  variant = 'primary',
  loading = false,
  disabled,
  children,
  startIcon,
  endIcon,
  ...props
}: ButtonProps) => {
  // Маппинг наших вариантов на MUI варианты
  const muiVariant = variant === 'primary' ? 'contained' : variant;

  return (
    <MuiButton
      variant={muiVariant}
      disabled={disabled || loading}
      startIcon={loading ? undefined : startIcon}
      endIcon={loading ? undefined : endIcon}
      {...props}
    >
      {loading ? (
        <>
          <CircularProgress
            size={20}
            sx={{
              color: variant === 'primary' ? 'white' : 'primary.main',
              mr: 1,
            }}
          />
          {children}
        </>
      ) : (
        children
      )}
    </MuiButton>
  );
};

export default Button;
