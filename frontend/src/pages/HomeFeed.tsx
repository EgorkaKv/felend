import { Container, Typography, Box } from '@mui/material';

const HomeFeed = () => {
  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Лента опросов
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Здесь будут отображаться доступные опросы
        </Typography>
      </Box>

      {/* Placeholder для карточек опросов */}
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary">
          🎯 Скоро здесь появятся опросы
        </Typography>
      </Box>
    </Container>
  );
};

export default HomeFeed;
