import { Badge, IconButton } from '@mui/material';
import { FilterList as FilterIcon } from '@mui/icons-material';

interface FilterButtonProps {
  activeFiltersCount: number;
  onClick: () => void;
}

export const FilterButton = ({ activeFiltersCount, onClick }: FilterButtonProps) => {
  return (
    <IconButton onClick={onClick} sx={{ bgcolor: 'background.paper' }}>
      <Badge badgeContent={activeFiltersCount} color="primary">
        <FilterIcon />
      </Badge>
    </IconButton>
  );
};

export default FilterButton;
