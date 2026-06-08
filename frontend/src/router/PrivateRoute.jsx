import { Navigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Spinner from '../shared/components/Spinner';

export default function PrivateRoute({ children }) {
  const { usuario, accessToken } = useAuthStore();
  const location = useLocation();

  // If no token at all, redirect to login
  if (!accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Token exists but user not yet loaded — show brief spinner
  if (!usuario) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return children;
}
