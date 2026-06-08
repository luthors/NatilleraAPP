import RecuperarPasswordForm from '../features/auth/components/RecuperarPasswordForm';

export default function RecuperarPasswordPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Natillera App</h1>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-5">Recuperar contraseña</h2>
          <RecuperarPasswordForm />
        </div>
      </div>
    </div>
  );
}
