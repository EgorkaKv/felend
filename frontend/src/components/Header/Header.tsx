import { Box, Typography, Tooltip } from '@mui/material';
import { AccountBalanceWallet as WalletIcon } from '@mui/icons-material';
import { useAppSelector } from '@/store/hooks';

export const Header = () => {
  const user = useAppSelector((state) => state.auth.user);
  const balance = user?.balance || 0;

  return (
    <Box
      component="header"
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: 2,
        px: 2,
        bgcolor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      {/* Логотип */}
      <Typography
        variant="h5"
        component="div"
        sx={{
          fontWeight: 700,
          color: 'primary.main',
        }}
      >
        Felend
      </Typography>

      {/* Баланс */}
      {user && (
        <Tooltip title="Ваш текущий баланс баллов">
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              bgcolor: 'primary.light',
              px: 1.5,
              py: 0.75,
              borderRadius: 2,
              cursor: 'pointer',
            }}
          >
            <WalletIcon sx={{ fontSize: 20, color: 'primary.main' }} />
            <Typography
              variant="body1"
              sx={{
                fontWeight: 600,
                color: 'primary.main',
              }}
            >
              {balance}
            </Typography>
          </Box>
        </Tooltip>
      )}
    </Box>
  );
};

export default Header;
