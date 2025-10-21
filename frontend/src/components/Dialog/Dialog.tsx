import {
  Dialog as MuiDialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import Button from '@/components/Button';

interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  content?: string | React.ReactNode;
  children?: React.ReactNode;
  // Для confirmation dialog
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm?: () => void;
  confirmColor?: 'primary' | 'error';
  loading?: boolean;
}

const Dialog = ({
  open,
  onClose,
  title,
  content,
  children,
  confirmLabel = 'Подтвердить',
  cancelLabel = 'Отмена',
  onConfirm,
  confirmColor = 'primary',
  loading = false,
}: DialogProps) => {
  const isConfirmation = !!onConfirm;

  return (
    <MuiDialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        },
      }}
    >
      <DialogTitle>{title}</DialogTitle>

      <DialogContent>
        {content && typeof content === 'string' ? (
          <DialogContentText>{content}</DialogContentText>
        ) : (
          content
        )}
        {children}
      </DialogContent>

      {isConfirmation && (
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button variant="text" onClick={onClose} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button
            variant="primary"
            onClick={onConfirm}
            loading={loading}
            color={confirmColor}
            autoFocus
          >
            {confirmLabel}
          </Button>
        </DialogActions>
      )}
    </MuiDialog>
  );
};

export default Dialog;
