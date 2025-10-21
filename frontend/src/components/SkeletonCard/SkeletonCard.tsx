import { Box, Skeleton, Card, CardContent } from '@mui/material';

const SkeletonCard = () => {
  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        {/* Награда */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Skeleton variant="circular" width={32} height={32} />
        </Box>

        {/* Название */}
        <Skeleton variant="text" width="80%" height={28} sx={{ mb: 1 }} />

        {/* Описание */}
        <Skeleton variant="text" width="100%" />
        <Skeleton variant="text" width="90%" sx={{ mb: 2 }} />

        {/* Категория и время */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Skeleton variant="rounded" width={80} height={24} />
          <Skeleton variant="rounded" width={100} height={24} />
        </Box>

        {/* Кнопка */}
        <Skeleton variant="rounded" width="100%" height={40} />
      </CardContent>
    </Card>
  );
};

export default SkeletonCard;
