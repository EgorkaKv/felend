import { useNavigate, useLocation } from 'react-router-dom';
import {
  BottomNavigation as MuiBottomNavigation,
  BottomNavigationAction,
  Paper,
} from '@mui/material';
import {
  Home as HomeIcon,
  Assignment as AssignmentIcon,
  AddCircle as AddCircleIcon,
  History as HistoryIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

const navigationItems = [
  { label: 'Главная', icon: <HomeIcon />, path: '/' },
  { label: 'Мои опросы', icon: <AssignmentIcon />, path: '/my-surveys' },
  { label: 'Добавить', icon: <AddCircleIcon />, path: '/add-survey' },
  { label: 'История', icon: <HistoryIcon />, path: '/history' },
  { label: 'Профиль', icon: <PersonIcon />, path: '/profile' },
];

export const BottomNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const currentIndex = navigationItems.findIndex(
    (item) => item.path === location.pathname
  );

  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    navigate(navigationItems[newValue].path);
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        display: { xs: 'block', md: 'none' }, // Скрываем на десктопе
      }}
      elevation={3}
    >
      <MuiBottomNavigation
        value={currentIndex === -1 ? 0 : currentIndex}
        onChange={handleChange}
        showLabels
      >
        {navigationItems.map((item) => (
          <BottomNavigationAction
            key={item.path}
            label={item.label}
            icon={item.icon}
          />
        ))}
      </MuiBottomNavigation>
    </Paper>
  );
};

export default BottomNavigation;
