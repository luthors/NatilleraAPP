import { Link, useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import apiClient from '../../lib/apiClient';

export default function AppLayout({ children }) {
  const { usuario, clearAuth } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (_) {
      // ignore
    }
    clearAuth();
    navigate('/login');
  };

  const navLinks = [
    { to: '/dashboard', label: 'Inicio' },
    { to: '/perfil', label: 'Mi perfil' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top nav */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/dashboard" className="font-bold text-primary text-lg">
            Natillera App
          </Link>
          <nav className="hidden sm:flex items-center gap-4 text-sm">
            {navLinks.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className={`px-2 py-1 rounded transition-colors ${
                  location.pathname === to
                    ? 'text-primary font-semibold'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {label}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-red-600 transition-colors px-2 py-1"
            >
              Salir
            </button>
          </nav>
          {/* Mobile user pill */}
          <div className="flex sm:hidden items-center gap-2">
            <span className="text-sm text-gray-600">{usuario?.nombre?.split(' ')[0]}</span>
            <button onClick={handleLogout} className="text-xs text-gray-400 hover:text-red-500">
              Salir
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-6">
        {children}
      </main>
    </div>
  );
}
