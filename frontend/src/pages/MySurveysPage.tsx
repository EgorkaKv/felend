import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useSWR from 'swr';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { default as MuiButton } from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { Add as AddIcon, MoreVert as MoreVertIcon } from '@mui/icons-material';
import { useDispatch } from 'react-redux';

import SurveyCard from '@/components/SurveyCard';
import EmptyState from '@/components/EmptyState';
import { getMySurveys, updateSurveyStatus, deleteSurvey } from '@/api/surveys';
import { showSnackbar } from '@/store/uiSlice';
import { getErrorMessage } from '@/utils/errorHandler';
import type { Survey } from '@/types';

type SurveyStatus = 'active' | 'paused' | 'completed';

function MySurveysPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState<SurveyStatus>('active');
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedSurvey, setSelectedSurvey] = useState<Survey | null>(null);

  const { data, error, isLoading, mutate } = useSWR<{ surveys: Survey[] }>(
    '/surveys/my',
    getMySurveys
  );

  const surveys = data?.surveys || [];
  const filteredSurveys = surveys.filter((survey) => survey.status === activeTab);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: SurveyStatus) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, survey: Survey) => {
    setMenuAnchor(event.currentTarget);
    setSelectedSurvey(survey);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedSurvey(null);
  };

  const handlePauseResume = async () => {
    if (!selectedSurvey) return;

    try {
      const newStatus = selectedSurvey.status === 'active' ? 'paused' : 'active';
      await updateSurveyStatus(selectedSurvey.id, newStatus);
      mutate();
      dispatch(
        showSnackbar({
          message: `Опрос ${newStatus === 'active' ? 'возобновлен' : 'приостановлен'}`,
          severity: 'success',
        })
      );
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch(
        showSnackbar({
          message: errorMessage,
          severity: 'error',
        })
      );
    } finally {
      handleMenuClose();
    }
  };

  const handleDelete = async () => {
    if (!selectedSurvey) return;

    if (!window.confirm('Вы уверены, что хотите удалить этот опрос?')) {
      handleMenuClose();
      return;
    }

    try {
      await deleteSurvey(selectedSurvey.id);
      mutate();
      dispatch(
        showSnackbar({
          message: 'Опрос удален',
          severity: 'success',
        })
      );
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch(
        showSnackbar({
          message: errorMessage,
          severity: 'error',
        })
      );
    } finally {
      handleMenuClose();
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">Ошибка загрузки опросов</Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          Мои опросы
        </Typography>
        <MuiButton
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/add-survey')}
        >
          Создать
        </MuiButton>
      </Box>

      {/* Tabs */}
      <Box mb={3}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Tab label="Активные" value="active" />
          <Tab label="Приостановлены" value="paused" />
          <Tab label="Завершенные" value="completed" />
        </Tabs>
      </Box>

      {/* Survey List */}
      {filteredSurveys.length === 0 ? (
        <EmptyState
          title="Нет опросов"
          subtitle={
            activeTab === 'active'
              ? 'Создайте свой первый опрос'
              : `Нет ${activeTab === 'paused' ? 'приостановленных' : 'завершенных'} опросов`
          }
          actionLabel={activeTab === 'active' ? 'Создать опрос' : undefined}
          onAction={activeTab === 'active' ? () => navigate('/add-survey') : undefined}
        />
      ) : (
        <Box display="flex" flexDirection="column" gap={2}>
          {filteredSurveys.map((survey) => (
            <Box key={survey.id} position="relative">
              <Box position="relative">
                <SurveyCard survey={survey} />
                <IconButton
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    bgcolor: 'background.paper',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                  onClick={(e) => handleMenuOpen(e, survey)}
                >
                  <MoreVertIcon />
                </IconButton>
              </Box>
            </Box>
          ))}
        </Box>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        {selectedSurvey?.status !== 'completed' && (
          <MenuItem onClick={handlePauseResume}>
            {selectedSurvey?.status === 'active' ? 'Приостановить' : 'Возобновить'}
          </MenuItem>
        )}
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          Удалить
        </MenuItem>
      </Menu>
    </Box>
  );
}

export default MySurveysPage;
