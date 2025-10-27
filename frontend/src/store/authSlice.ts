import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  verificationToken: string | null; // Для процесса верификации email
}

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  verificationToken: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setTokens: (state, action: PayloadAction<{ accessToken: string; refreshToken: string }>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
    setVerificationToken: (state, action: PayloadAction<string>) => {
      state.verificationToken = action.payload;
    },
    updateUserBalance: (state, action: PayloadAction<number>) => {
      if (state.user) {
        state.user.balance = action.payload;
      }
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.verificationToken = null;
    },
  },
});

export const { setTokens, setUser, setVerificationToken, updateUserBalance, logout } = authSlice.actions;
export default authSlice.reducer;
