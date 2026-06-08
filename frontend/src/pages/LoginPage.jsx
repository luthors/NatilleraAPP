import LoginForm from '../features/auth/components/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Natillera App</h1>
          <p className="text-gray-500 text-sm mt-1">Plataforma de ahorro comunitario</p>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-5">Iniciar sesión</h2>
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
