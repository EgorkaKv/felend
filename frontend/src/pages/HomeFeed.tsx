import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useSWR from 'swr';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Alert from '@mui/material/Alert';
import SearchBar from '@/components/SearchBar';
import FilterButton from '@/components/FilterButton';
import FilterModal from '@/components/FilterModal';
import SurveyCard from '@/components/SurveyCard';
import SkeletonCard from '@/components/SkeletonCard';
import EmptyState from '@/components/EmptyState';
import { getSurveys } from '@/api/surveys';
import { getCategories } from '@/api/categories';
import type { SurveyFilters } from '@/types';

const HomeFeed = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<SurveyFilters>({});
  const [filterModalOpen, setFilterModalOpen] = useState(false);

  // Получение категорий
  const { data: categoriesData } = useSWR(
    '/categories',
    async () => {
      const data = await getCategories();
      return data.categories;
    }
  );
  const categories = categoriesData || [];

  // Формирование параметров запроса
  const queryParams: SurveyFilters = {
    search: search || undefined,
    ...filters,
  };

  // Получение опросов
  const {
    data: surveysData,
    error,
    isLoading,
  } = useSWR(
    ['/surveys', JSON.stringify(queryParams)],
    async () => {
      const data = await getSurveys(queryParams);
      return data.surveys;
    },
    {
      revalidateOnFocus: false,
      dedupingInterval: 30000, // 30 секунд
    }
  );

  const surveys = surveysData || [];

  // Подсчет активных фильтров
  const activeFiltersCount = Object.keys(filters).filter(
    (key) => filters[key as keyof SurveyFilters] !== undefined
  ).length;

  const handleParticipate = (surveyId: number) => {
    navigate(`/survey/${surveyId}/complete`);
  };

  const handleApplyFilters = (newFilters: SurveyFilters) => {
    setFilters(newFilters);
  };

  // Loading state
  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 3 }}>
        {/* Поиск и фильтры */}
        <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
          <Box sx={{ flex: 1 }}>
            <SearchBar value={search} onChange={setSearch} />
          </Box>
          <FilterButton
            activeFiltersCount={activeFiltersCount}
            onClick={() => setFilterModalOpen(true)}
          />
        </Box>

        {/* Skeleton cards */}
        <Stack spacing={2}>
          {[1, 2, 3].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </Stack>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Ошибка загрузки опросов. Попробуйте обновить страницу.
        </Alert>
      </Container>
    );
  }

  // Empty state
  if (!surveys || surveys.length === 0) {
    const hasActiveFilters = search || activeFiltersCount > 0;

    return (
      <Container maxWidth="md" sx={{ py: 3 }}>
        {/* Поиск и фильтры */}
        <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
          <Box sx={{ flex: 1 }}>
            <SearchBar value={search} onChange={setSearch} />
          </Box>
          <FilterButton
            activeFiltersCount={activeFiltersCount}
            onClick={() => setFilterModalOpen(true)}
          />
        </Box>

        <EmptyState
          title={hasActiveFilters ? 'Ничего не найдено' : 'Нет доступных опросов'}
          subtitle={
            hasActiveFilters
              ? 'Попробуйте изменить параметры поиска или фильтры'
              : 'Новые опросы появятся совсем скоро'
          }
          actionLabel={hasActiveFilters ? 'Сбросить фильтры' : undefined}
          onAction={
            hasActiveFilters
              ? () => {
                  setSearch('');
                  setFilters({});
                }
              : undefined
          }
        />

        <FilterModal
          open={filterModalOpen}
          onClose={() => setFilterModalOpen(false)}
          filters={filters}
          onApply={handleApplyFilters}
          categories={categories}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      {/* Поиск и фильтры */}
      <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <SearchBar value={search} onChange={setSearch} />
        </Box>
        <FilterButton
          activeFiltersCount={activeFiltersCount}
          onClick={() => setFilterModalOpen(true)}
        />
      </Box>

      {/* Список карточек */}
      <Stack spacing={2}>
        {surveys.map((survey) => (
          <SurveyCard key={survey.id} survey={survey} onParticipate={handleParticipate} />
        ))}
      </Stack>

      {/* Filter Modal */}
      <FilterModal
        open={filterModalOpen}
        onClose={() => setFilterModalOpen(false)}
        filters={filters}
        onApply={handleApplyFilters}
        categories={categories}
      />
    </Container>
  );
};

export default HomeFeed;
