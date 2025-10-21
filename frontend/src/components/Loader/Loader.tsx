import { Box, CircularProgress } from '@mui/material';

interface LoaderProps {
  size?: number;
  fullScreen?: boolean;
}

const Loader = ({ size = 40, fullScreen = true }: LoaderProps) => {
  if (fullScreen) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        <CircularProgress size={size} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        py: 4,
      }}
    >
      <CircularProgress size={size} />
    </Box>
  );
};

export default Loader;
