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
          pb: { xs: 8, md: 0 }, // Padding bottom для Bottom Navigation на мобильных
          overflow: 'auto',
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
