import { Navigate } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';

interface PublicRouteProps {
  children: React.ReactNode;
}

// Публичный маршрут - redirect если уже авторизован
const PublicRoute = ({ children }: PublicRouteProps) => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  if (isAuthenticated) {
    // Redirect на главную если уже залогинен
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default PublicRoute;
