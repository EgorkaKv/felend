import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from '@/components/PublicRoute';
import Snackbar from '@/components/Snackbar';
import MainLayout from '@/components/Layout';

// Pages
import WelcomeScreen from '@/pages/WelcomeScreen';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import ConfirmEmailPage from '@/pages/ConfirmEmailPage';
import HomeFeed from '@/pages/HomeFeed';

function App() {
  return (
    <>
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
          <Route path="/my-surveys" element={<div>My Surveys - TODO</div>} />
          <Route path="/add-survey" element={<div>Add Survey - TODO</div>} />
          <Route path="/history" element={<div>History - TODO</div>} />
          <Route path="/profile" element={<div>Profile - TODO</div>} />
        </Route>

        {/* Fallback - redirect на главную */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Global Snackbar */}
      <Snackbar />
    </>
  );
}

export default App;
