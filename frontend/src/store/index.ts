import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // localStorage
import authReducer from './authSlice';
import uiReducer from './uiSlice';

// Конфигурация для redux-persist
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth'], // Только auth будет сохраняться в localStorage
};

// Комбинируем редюсеры
const rootReducer = combineReducers({
  auth: authReducer,
  ui: uiReducer,
});

// Создаем персистентный редюсер
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Создаем store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Игнорируем redux-persist actions
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

// Создаем persistor
export const persistor = persistStore(store);

// Типы для TypeScript
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
