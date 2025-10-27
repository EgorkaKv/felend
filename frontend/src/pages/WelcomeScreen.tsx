import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import {
  Poll as PollIcon,
  AccountBalanceWallet as WalletIcon,
  PeopleAlt as PeopleIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination, Navigation } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper';
import Button from '@/components/Button';
import '../styles/swiper.css';

const ONBOARDING_SHOWN_KEY = 'felend_onboarding_shown';

interface Slide {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

const slides: Slide[] = [
  {
    icon: <PollIcon sx={{ fontSize: 120 }} />,
    title: 'Проходите опросы',
    description:
      'Заполняйте интересные опросы от разных брендов и компаний. Ваше мнение действительно важно!',
    color: '#4D96FF',
  },
  {
    icon: <WalletIcon sx={{ fontSize: 120 }} />,
    title: 'Зарабатывайте баллы',
    description:
      'Получайте баллы за каждый пройденный опрос. Накапливайте их и обменивайте на реальные деньги!',
    color: '#6BCF7F',
  },
  {
    icon: <PeopleIcon sx={{ fontSize: 120 }} />,
    title: 'Создавайте свои опросы',
    description:
      'Нужно узнать мнение людей? Создайте свой опрос, установите награду и получите ответы от реальных пользователей!',
    color: '#FFB84D',
  },
];

const WelcomeScreen = () => {
  const navigate = useNavigate();
  const [swiperInstance, setSwiperInstance] = useState<SwiperType | null>(null);
  const [isLastSlide, setIsLastSlide] = useState(false);

  useEffect(() => {
    // Проверяем, был ли уже показан onboarding
    const onboardingShown = localStorage.getItem(ONBOARDING_SHOWN_KEY);
    if (onboardingShown) {
      navigate('/register', { replace: true });
    }
  }, [navigate]);

  const handleSkip = () => {
    localStorage.setItem(ONBOARDING_SHOWN_KEY, 'true');
    navigate('/register');
  };

  const handleNext = () => {
    if (isLastSlide) {
      handleSkip();
    } else {
      swiperInstance?.slideNext();
    }
  };

  const handleSlideChange = (swiper: SwiperType) => {
    setIsLastSlide(swiper.isEnd);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Кнопка Skip */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          p: 2,
        }}
      >
        <Button variant="text" onClick={handleSkip}>
          Пропустить
        </Button>
      </Box>

      {/* Слайды */}
      <Container
        maxWidth="sm"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Swiper
          modules={[Pagination, Navigation]}
          spaceBetween={50}
          slidesPerView={1}
          pagination={{ clickable: true }}
          onSwiper={setSwiperInstance}
          onSlideChange={handleSlideChange}
          style={{ width: '100%', height: '100%' }}
        >
          {slides.map((slide, index) => (
            <SwiperSlide key={index}>
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  px: 2,
                  height: '100%',
                  justifyContent: 'center',
                }}
              >
                {/* Иконка */}
                <Box
                  sx={{
                    color: slide.color,
                    mb: 4,
                  }}
                >
                  {slide.icon}
                </Box>

                {/* Заголовок */}
                <Typography
                  variant="h4"
                  component="h1"
                  gutterBottom
                  sx={{
                    fontWeight: 600,
                    mb: 2,
                  }}
                >
                  {slide.title}
                </Typography>

                {/* Описание */}
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{
                    maxWidth: 400,
                    fontSize: '1.1rem',
                    lineHeight: 1.6,
                  }}
                >
                  {slide.description}
                </Typography>
              </Box>
            </SwiperSlide>
          ))}
        </Swiper>
      </Container>

      {/* Кнопка Далее */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          p: 4,
        }}
      >
        <IconButton
          onClick={handleNext}
          sx={{
            bgcolor: 'primary.main',
            color: 'white',
            width: 64,
            height: 64,
            '&:hover': {
              bgcolor: 'primary.dark',
            },
          }}
        >
          <ArrowForwardIcon sx={{ fontSize: 32 }} />
        </IconButton>
      </Box>
    </Box>
  );
};

export default WelcomeScreen;
