import { useRef, useEffect } from 'react';
import type { KeyboardEvent, ClipboardEvent } from 'react';
import { Box, TextField } from '@mui/material';

interface PinInputProps {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: boolean;
  autoFocus?: boolean;
}

export const PinInput = ({
  length = 6,
  value,
  onChange,
  disabled = false,
  error = false,
  autoFocus = false,
}: PinInputProps) => {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (autoFocus && inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [autoFocus]);

  const handleChange = (index: number, newValue: string) => {
    // Разрешаем только цифры
    if (newValue && !/^\d$/.test(newValue)) {
      return;
    }

    const newPin = value.split('');
    newPin[index] = newValue;
    const updatedValue = newPin.join('');

    onChange(updatedValue);

    // Автоматический переход к следующему полю
    if (newValue && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Backspace') {
      if (!value[index] && index > 0) {
        // Если поле пустое, переходим к предыдущему
        inputRefs.current[index - 1]?.focus();
      } else {
        // Удаляем текущий символ
        const newPin = value.split('');
        newPin[index] = '';
        onChange(newPin.join(''));
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: ClipboardEvent<HTMLDivElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text/plain');
    const digits = pastedData.replace(/\D/g, '').slice(0, length);
    onChange(digits);

    // Фокус на следующее пустое поле или последнее
    const nextIndex = Math.min(digits.length, length - 1);
    inputRefs.current[nextIndex]?.focus();
  };

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1,
        justifyContent: 'center',
      }}
    >
      {Array.from({ length }).map((_, index) => (
        <TextField
          key={index}
          inputRef={(el) => {
            inputRefs.current[index] = el;
          }}
          value={value[index] || ''}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          error={error}
          inputProps={{
            maxLength: 1,
            style: {
              textAlign: 'center',
              fontSize: '1.5rem',
              fontWeight: 600,
              padding: '12px',
            },
          }}
          sx={{
            width: 48,
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderWidth: 2,
                borderColor: error ? 'error.main' : 'divider',
              },
              '&:hover fieldset': {
                borderColor: error ? 'error.main' : 'primary.main',
              },
              '&.Mui-focused fieldset': {
                borderColor: error ? 'error.main' : 'primary.main',
              },
            },
          }}
        />
      ))}
    </Box>
  );
};

export default PinInput;
