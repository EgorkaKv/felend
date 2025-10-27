import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from '@/components/PublicRoute';
import Snackbar from '@/components/Snackbar';
import MainLayout from '@/components/Layout';
import DevTools from '@/components/DevTools';
import Loader from '@/components/Loader';

// Lazy load pages for code splitting
const WelcomeScreen = lazy(() => import('@/pages/WelcomeScreen'));
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const ConfirmEmailPage = lazy(() => import('@/pages/ConfirmEmailPage'));
const HomeFeed = lazy(() => import('@/pages/HomeFeed'));
const SurveyCompletionPage = lazy(() => import('@/pages/SurveyCompletionPage'));
const AddSurveyPage = lazy(() => import('@/pages/AddSurveyPage'));
const MySurveysPage = lazy(() => import('@/pages/MySurveysPage'));
const HistoryPage = lazy(() => import('@/pages/HistoryPage'));
const ProfilePage = lazy(() => import('@/pages/ProfilePage'));

function App() {
  return (
    <>
      <Suspense fallback={<Loader />}>
        <Routes>
        {/* Публичные маршруты (без Layout) */}
        <Route
          path="/welcome"
          element={
            <PublicRoute>
              <WelcomeScreen />
            </PublicRoute>
          }
        />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />
        <Route path="/confirm-email" element={<ConfirmEmailPage />} />

        {/* Защищенные маршруты с Layout */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<HomeFeed />} />
          <Route path="/survey/:id/complete" element={<SurveyCompletionPage />} />
          <Route path="/my-surveys" element={<MySurveysPage />} />
          <Route path="/add-survey" element={<AddSurveyPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        {/* Fallback - redirect на главную */}
        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>

      {/* Global Snackbar */}
      <Snackbar />
      
      {/* Dev Tools (only in dev mode) */}
      <DevTools />
    </>
  );
}

export default App;
