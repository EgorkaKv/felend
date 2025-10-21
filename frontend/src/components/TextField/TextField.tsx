import { TextField as MuiTextField, InputAdornment, IconButton } from '@mui/material';
import type { TextFieldProps as MuiTextFieldProps } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useState } from 'react';
import { Controller } from 'react-hook-form';
import type { Control, FieldValues, Path } from 'react-hook-form';

interface TextFieldProps<T extends FieldValues> extends Omit<MuiTextFieldProps, 'name'> {
  name: Path<T>;
  control?: Control<T>;
  showPasswordToggle?: boolean;
}

function TextField<T extends FieldValues>({
  name,
  control,
  type = 'text',
  showPasswordToggle = false,
  ...props
}: TextFieldProps<T>) {
  const [showPassword, setShowPassword] = useState(false);

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  // Определяем тип поля
  const fieldType = showPasswordToggle && showPassword ? 'text' : type;

  // Если передан control (React Hook Form), используем Controller
  if (control) {
    return (
      <Controller
        name={name}
        control={control}
        render={({ field, fieldState }) => (
          <MuiTextField
            {...field}
            {...props}
            type={fieldType}
            error={!!fieldState.error}
            helperText={fieldState.error?.message || props.helperText}
            fullWidth
            InputProps={{
              ...props.InputProps,
              endAdornment: showPasswordToggle ? (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePassword}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ) : (
                props.InputProps?.endAdornment
              ),
            }}
          />
        )}
      />
    );
  }

  // Без React Hook Form - обычный TextField
  return (
    <MuiTextField
      {...props}
      type={fieldType}
      fullWidth
      InputProps={{
        ...props.InputProps,
        endAdornment: showPasswordToggle ? (
          <InputAdornment position="end">
            <IconButton
              aria-label="toggle password visibility"
              onClick={handleTogglePassword}
              edge="end"
            >
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </IconButton>
          </InputAdornment>
        ) : (
          props.InputProps?.endAdornment
        ),
      }}
    />
  );
}

export default TextField;
