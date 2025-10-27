import { Navigate } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';

interface PublicRouteProps {
  children: React.ReactNode;
}

// Публичный маршрут - redirect если уже авторизован
const PublicRoute = ({ children }: PublicRouteProps) => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  if (import.meta.env.DEV) {
    console.log('%c[PublicRoute] Check', 'color: #9B59B6; font-weight: bold', {
      isAuthenticated,
      currentPath: window.location.pathname,
      willRedirect: isAuthenticated,
    });
  }

  if (isAuthenticated) {
    if (import.meta.env.DEV) {
      console.log('%c[PublicRoute] User is authenticated, redirecting to /', 'color: #9B59B6; font-weight: bold');
    }
    // Redirect на главную если уже залогинен
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default PublicRoute;
