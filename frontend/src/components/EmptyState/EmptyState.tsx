import { Box, Typography } from '@mui/material';
import type { SvgIconComponent } from '@mui/icons-material';
import Button from '@/components/Button';

interface EmptyStateProps {
  icon?: SvgIconComponent;
  title: string;
  subtitle?: string;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState = ({ icon: Icon, title, subtitle, actionLabel, onAction }: EmptyStateProps) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
      }}
    >
      {Icon && (
        <Icon
          sx={{
            fontSize: 80,
            color: 'text.disabled',
            mb: 2,
          }}
        />
      )}

      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
        {title}
      </Typography>

      {subtitle && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
          {subtitle}
        </Typography>
      )}

      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;
