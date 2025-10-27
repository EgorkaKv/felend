import { useState } from 'react';
import useSWR from 'swr';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Receipt as ReceiptIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

import EmptyState from '@/components/EmptyState';
import { getUserTransactions as getTransactions } from '@/api/users';
import type { Transaction } from '@/types';

type TransactionFilter = 'all' | 'earned' | 'spent';

function HistoryPage() {
  const [filter, setFilter] = useState<TransactionFilter>('all');

  const { data, error, isLoading } = useSWR<{ transactions: Transaction[] }>(
    '/users/me/transactions',
    getTransactions
  );

  const transactions = data?.transactions || [];
  const filteredTransactions = transactions.filter((t) => {
    if (filter === 'earned') return t.type === 'earned';
    if (filter === 'spent') return t.type === 'spent';
    return true;
  });

  const handleFilterChange = (_event: React.MouseEvent<HTMLElement>, newFilter: TransactionFilter | null) => {
    if (newFilter !== null) {
      setFilter(newFilter);
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
        <Alert severity="error">Ошибка загрузки истории транзакций</Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          История транзакций
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Все ваши начисления и списания баллов
        </Typography>
      </Box>

      {/* Filters */}
      {transactions.length > 0 && (
        <Box mb={3} display="flex" justifyContent="center">
          <ToggleButtonGroup
            value={filter}
            exclusive
            onChange={handleFilterChange}
            aria-label="filter transactions"
          >
            <ToggleButton value="all" aria-label="all">
              Все
            </ToggleButton>
            <ToggleButton value="earned" aria-label="earned">
              Заработано
            </ToggleButton>
            <ToggleButton value="spent" aria-label="spent">
              Потрачено
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      )}

      {/* Transactions List */}
      {filteredTransactions.length === 0 ? (
        <EmptyState
          icon={ReceiptIcon}
          title="Нет транзакций"
          subtitle={
            filter === 'all'
              ? 'Начните проходить опросы, чтобы зарабатывать баллы'
              : `Нет ${filter === 'earned' ? 'заработанных' : 'потраченных'} баллов`
          }
        />
      ) : (
        <List>
          {filteredTransactions.map((transaction) => {
            const isPositive = transaction.amount > 0;
            const date = new Date(transaction.created_at);

            return (
              <ListItem
                key={transaction.id}
                sx={{
                  bgcolor: 'background.paper',
                  borderRadius: 2,
                  mb: 1,
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <ListItemAvatar>
                  <Avatar
                    sx={{
                      bgcolor: isPositive ? 'success.light' : 'error.light',
                      color: isPositive ? 'success.dark' : 'error.dark',
                    }}
                  >
                    {isPositive ? <AddIcon /> : <RemoveIcon />}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body1" fontWeight="medium">
                        {transaction.description}
                      </Typography>
                      <Chip
                        label={`${isPositive ? '+' : ''}${transaction.amount} ₽`}
                        color={isPositive ? 'success' : 'error'}
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {format(date, 'dd MMMM yyyy, HH:mm', { locale: ru })}
                    </Typography>
                  }
                />
              </ListItem>
            );
          })}
        </List>
      )}
    </Box>
  );
}

export default HistoryPage;
