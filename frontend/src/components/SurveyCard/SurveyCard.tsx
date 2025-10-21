import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import {
  AccessTime as TimeIcon,
  CheckCircle as CheckIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import Button from '@/components/Button';
import type { Survey } from '@/types';

interface SurveyCardProps {
  survey: Survey;
  onParticipate?: (surveyId: number) => void;
  loading?: boolean;
}

export const SurveyCard = ({ survey, onParticipate, loading = false }: SurveyCardProps) => {
  const {
    id,
    title,
    description,
    reward,
    category,
    estimated_time,
    is_suitable,
    is_completed,
    theme_color,
  } = survey;

  const handleClick = () => {
    if (onParticipate && is_suitable && !is_completed) {
      onParticipate(id);
    }
  };

  const getButtonText = () => {
    if (is_completed) return 'Пройдено';
    if (!is_suitable) return 'Не подходит';
    return 'Пройти опрос';
  };

  const getButtonIcon = () => {
    if (is_completed) return <CheckIcon />;
    if (!is_suitable) return <BlockIcon />;
    return undefined;
  };

  return (
    <Card
      sx={{
        position: 'relative',
        overflow: 'visible',
        borderRadius: 2,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: is_suitable && !is_completed ? 'translateY(-4px)' : 'none',
          boxShadow: is_suitable && !is_completed ? 4 : 1,
        },
        bgcolor: theme_color || 'background.paper',
        opacity: !is_suitable || is_completed ? 0.7 : 1,
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        {/* Награда */}
        <Box
          sx={{
            position: 'absolute',
            top: -12,
            right: 16,
            bgcolor: 'primary.main',
            color: 'white',
            px: 2,
            py: 0.5,
            borderRadius: 2,
            boxShadow: 2,
          }}
        >
          <Typography variant="h6" component="span" sx={{ fontWeight: 700 }}>
            +{reward}
          </Typography>
          <Typography variant="caption" component="span" sx={{ ml: 0.5 }}>
            баллов
          </Typography>
        </Box>

        {/* Категория и время */}
        <Box sx={{ display: 'flex', gap: 1, mb: 1.5, mt: 1 }}>
          {category && (
            <Chip
              label={category}
              size="small"
              sx={{
                bgcolor: 'secondary.light',
                color: 'secondary.main',
                fontWeight: 500,
              }}
            />
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <TimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              {estimated_time} мин
            </Typography>
          </Box>
        </Box>

        {/* Заголовок */}
        <Typography
          variant="h6"
          component="h3"
          gutterBottom
          sx={{
            fontWeight: 600,
            mb: 1,
            lineHeight: 1.3,
          }}
        >
          {title}
        </Typography>

        {/* Описание */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            lineHeight: 1.5,
          }}
        >
          {description}
        </Typography>

        {/* Кнопка */}
        <Button
          variant={is_suitable && !is_completed ? 'primary' : 'outlined'}
          fullWidth
          onClick={handleClick}
          disabled={!is_suitable || is_completed || loading}
          loading={loading}
          startIcon={getButtonIcon()}
        >
          {getButtonText()}
        </Button>

        {/* Статус "Пройдено" */}
        {is_completed && (
          <Box
            sx={{
              position: 'absolute',
              top: 16,
              left: 16,
              bgcolor: 'success.main',
              color: 'white',
              px: 1.5,
              py: 0.5,
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            <CheckIcon sx={{ fontSize: 16 }} />
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              Пройдено
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default SurveyCard;
