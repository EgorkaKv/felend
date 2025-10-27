import { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Switch from '@mui/material/Switch';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import Drawer from '@mui/material/Drawer';
import Button from '@/components/Button';
import type { SurveyFilters, Category } from '@/types';

interface FilterModalProps {
  open: boolean;
  onClose: () => void;
  filters: SurveyFilters;
  onApply: (filters: SurveyFilters) => void;
  categories: Category[];
}

const durationOptions = [
  { value: 'short', label: 'До 5 минут' },
  { value: 'medium', label: '5-10 минут' },
  { value: 'long', label: 'Больше 10 минут' },
];

export const FilterModal = ({
  open,
  onClose,
  filters,
  onApply,
  categories,
}: FilterModalProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [localFilters, setLocalFilters] = useState<SurveyFilters>(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters, open]);

  const handleCategoryChange = (categoryId: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      category: prev.category === categoryId ? undefined : categoryId,
    }));
  };

  const handleDurationChange = (duration: 'short' | 'medium' | 'long') => {
    setLocalFilters((prev) => ({
      ...prev,
      duration: prev.duration === duration ? undefined : duration,
    }));
  };

  const handleRewardChange = (_event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    setLocalFilters((prev) => ({
      ...prev,
      min_reward: min,
      max_reward: max,
    }));
  };

  const handleOnlySuitableChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLocalFilters((prev) => ({
      ...prev,
      only_suitable: event.target.checked,
    }));
  };

  const handleReset = () => {
    setLocalFilters({});
  };

  const handleApply = () => {
    onApply(localFilters);
    onClose();
  };

  const content = (
    <>
      {/* Только подходящие */}
      <Box sx={{ mb: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={localFilters.only_suitable || false}
              onChange={handleOnlySuitableChange}
            />
          }
          label="Только подходящие мне"
        />
      </Box>

      {/* Категории */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
          Категория
        </Typography>
        <FormGroup>
          {categories.map((category) => (
            <FormControlLabel
              key={category.id}
              control={
                <Checkbox
                  checked={localFilters.category === category.id}
                  onChange={() => handleCategoryChange(category.id)}
                />
              }
              label={category.name}
            />
          ))}
        </FormGroup>
      </Box>

      {/* Награда */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
          Награда (баллов)
        </Typography>
        <Box sx={{ px: 1 }}>
          <Slider
            value={[localFilters.min_reward || 0, localFilters.max_reward || 1000]}
            onChange={handleRewardChange}
            valueLabelDisplay="auto"
            min={0}
            max={1000}
            step={10}
          />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {localFilters.min_reward || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {localFilters.max_reward || 1000}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Длительность */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
          Время прохождения
        </Typography>
        <FormGroup>
          {durationOptions.map((option) => (
            <FormControlLabel
              key={option.value}
              control={
                <Checkbox
                  checked={localFilters.duration === option.value}
                  onChange={() =>
                    handleDurationChange(option.value as 'short' | 'medium' | 'long')
                  }
                />
              }
              label={option.label}
            />
          ))}
        </FormGroup>
      </Box>
    </>
  );

  // На мобильных используем Drawer (снизу), на десктопе Dialog
  if (isMobile) {
    return (
      <Drawer anchor="bottom" open={open} onClose={onClose}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            Фильтры
          </Typography>
          {content}
          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            <Button variant="outlined" fullWidth onClick={handleReset}>
              Сбросить
            </Button>
            <Button variant="primary" fullWidth onClick={handleApply}>
              Применить
            </Button>
          </Box>
        </Box>
      </Drawer>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 600 }}>Фильтры</DialogTitle>
      <DialogContent>{content}</DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button variant="outlined" onClick={handleReset}>
          Сбросить
        </Button>
        <Button variant="primary" onClick={handleApply}>
          Применить
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FilterModal;
