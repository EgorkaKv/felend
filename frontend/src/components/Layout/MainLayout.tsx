import { Outlet } from 'react-router-dom';
import Box from '@mui/material/Box';
import Header from '@/components/Header';
import BottomNavigation from '@/components/BottomNavigation';

export const MainLayout = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <Header />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flex: 1,
          // Padding для bottom navigation + safe area для iPhone
          pb: { 
            xs: 'calc(64px + env(safe-area-inset-bottom))', 
            md: 0 
          },
          pt: { xs: 2, md: 0 }, // Небольшой отступ сверху на мобильных
          overflow: 'auto',
          // Smooth scroll на мобильных
          WebkitOverflowScrolling: 'touch',
        }}
      >
        <Outlet />
      </Box>

      {/* Bottom Navigation (только на мобильных) */}
      <BottomNavigation />
    </Box>
  );
};

export default MainLayout;
