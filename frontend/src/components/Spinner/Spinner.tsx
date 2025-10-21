import { CircularProgress, Box } from '@mui/material';
import type { CircularProgressProps } from '@mui/material';

interface SpinnerProps extends CircularProgressProps {
  inline?: boolean;
}

const Spinner = ({ size = 20, inline = false, ...props }: SpinnerProps) => {
  if (inline) {
    return <CircularProgress size={size} {...props} />;
  }

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
      <CircularProgress size={size} {...props} />
    </Box>
  );
};

export default Spinner;
