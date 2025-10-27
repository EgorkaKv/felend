import { useState } from 'react';
import { Box, Typography, IconButton, Collapse, Paper, Chip } from '@mui/material';
import { BugReport, Close, ExpandMore, ExpandLess } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import type { RootState } from '@/store';

/**
 * DevTools - компонент для отладки в dev mode
 * Показывает текущее состояние авторизации, API endpoint и другую полезную информацию
 */
const DevTools = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  
  const { isAuthenticated, user, accessToken, refreshToken } = useSelector(
    (state: RootState) => state.auth
  );

  // Показываем только в dev mode
  if (!import.meta.env.DEV) {
    return null;
  }

  if (!isOpen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          bottom: 80,
          right: 16,
          zIndex: 9999,
        }}
      >
        <IconButton
          onClick={() => setIsOpen(true)}
          sx={{
            bgcolor: '#FF6B6B',
            color: 'white',
            '&:hover': {
              bgcolor: '#FF5252',
            },
            boxShadow: 3,
          }}
        >
          <BugReport />
        </IconButton>
      </Box>
    );
  }

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 80,
        right: 16,
        width: 350,
        maxHeight: '60vh',
        overflow: 'auto',
        zIndex: 9999,
        p: 2,
        bgcolor: 'rgba(0, 0, 0, 0.9)',
        color: 'white',
        boxShadow: 6,
      }}
    >
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <BugReport sx={{ color: '#FF6B6B' }} />
          <Typography variant="h6" fontWeight="bold">
            Dev Tools
          </Typography>
        </Box>
        <Box>
          <IconButton size="small" onClick={() => setIsExpanded(!isExpanded)} sx={{ color: 'white' }}>
            {isExpanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
          <IconButton size="small" onClick={() => setIsOpen(false)} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </Box>
      </Box>

      {/* Quick Info */}
      <Box mb={2}>
        <Box display="flex" gap={1} mb={1}>
          <Chip
            label={isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
            color={isAuthenticated ? 'success' : 'error'}
            size="small"
          />
          <Chip
            label={`API: ${import.meta.env.VITE_API_BASE_URL?.split('/api')[0] || 'Not Set'}`}
            size="small"
            sx={{ bgcolor: '#4D96FF', color: 'white' }}
          />
        </Box>
      </Box>

      {/* Expanded Info */}
      <Collapse in={isExpanded}>
        <Box sx={{ fontSize: '0.875rem' }}>
          {/* Auth State */}
          <Typography variant="subtitle2" fontWeight="bold" sx={{ color: '#4D96FF', mb: 1 }}>
            Authentication:
          </Typography>
          <Box mb={2} sx={{ pl: 1 }}>
            <Typography variant="body2">
              Status: <strong>{isAuthenticated ? '✓ Authenticated' : '✗ Not authenticated'}</strong>
            </Typography>
            {user && (
              <>
                <Typography variant="body2">Email: {user.email}</Typography>
                <Typography variant="body2">ID: {user.id}</Typography>
                <Typography variant="body2">Balance: {user.balance} ₽</Typography>
              </>
            )}
            <Typography variant="body2">
              Access Token: {accessToken ? '✓ Present' : '✗ Missing'}
            </Typography>
            <Typography variant="body2">
              Refresh Token: {refreshToken ? '✓ Present' : '✗ Missing'}
            </Typography>
          </Box>

          {/* Environment */}
          <Typography variant="subtitle2" fontWeight="bold" sx={{ color: '#4D96FF', mb: 1 }}>
            Environment:
          </Typography>
          <Box mb={2} sx={{ pl: 1 }}>
            <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
              API URL: {import.meta.env.VITE_API_BASE_URL || 'Not set'}
            </Typography>
            <Typography variant="body2">
              Mode: {import.meta.env.MODE}
            </Typography>
            <Typography variant="body2">
              Dev: {import.meta.env.DEV ? 'Yes' : 'No'}
            </Typography>
          </Box>

          {/* Debug Tips */}
          <Typography variant="subtitle2" fontWeight="bold" sx={{ color: '#6BCF7F', mb: 1 }}>
            Debug Tips:
          </Typography>
          <Box sx={{ pl: 1, fontSize: '0.75rem' }}>
            <Typography variant="caption" display="block">
              • Открыть Console (F12) для подробных логов
            </Typography>
            <Typography variant="caption" display="block">
              • Проверить Network tab для API запросов
            </Typography>
            <Typography variant="caption" display="block">
              • Redux DevTools для состояния приложения
            </Typography>
          </Box>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default DevTools;
