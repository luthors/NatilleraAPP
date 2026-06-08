import { useParams, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import apiClient from '../lib/apiClient';
import useAuthStore from '../store/authStore';
import Spinner from '../shared/components/Spinner';

export default function AceptarInvitacion() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { accessToken } = useAuthStore();

  const { mutate, isPending, isSuccess, error, isIdle } = useMutation({
    mutationFn: async () => {
      // We need natilleraId but API accepts token under /socios/aceptar-invitacion/:token
      // The endpoint structure is /natilleras/{id}/socios/aceptar-invitacion/{token}
      // Since we don't know natilleraId from the URL, use a public lookup endpoint pattern
      // that accepts just the token via a dedicated route
      const { data } = await apiClient.post(`/invitaciones/${token}/aceptar`);
      return data;
    },
  });

  if (!accessToken) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-sm w-full text-center space-y-4">
          <p className="text-2xl">📩</p>
          <h2 className="text-lg font-semibold text-gray-900">Invitación a Natillera</h2>
          <p className="text-sm text-gray-600">
            Debes iniciar sesión o crear una cuenta para aceptar esta invitación.
          </p>
          <div className="flex gap-3">
            <a
              href={`/login?redirect=/invitacion/${token}`}
              className="flex-1 rounded-lg bg-primary text-white py-2 text-sm font-semibold text-center hover:bg-primary/90 transition-colors"
            >
              Iniciar sesión
            </a>
            <a
              href={`/register?redirect=/invitacion/${token}`}
              className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold text-center hover:bg-gray-50 transition-colors"
            >
              Registrarse
            </a>
          </div>
        </div>
      </div>
    );
  }

  const serverError = error?.response?.data?.detail || error?.message;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-sm w-full text-center space-y-5">
        <p className="text-3xl">🤝</p>
        <h2 className="text-lg font-semibold text-gray-900">Unirte a la Natillera</h2>

        {isIdle && (
          <>
            <p className="text-sm text-gray-600">
              Haz clic en el botón para aceptar la invitación y unirte a la natillera.
            </p>
            <button
              onClick={() => mutate()}
              className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
            >
              Aceptar invitación
            </button>
          </>
        )}

        {isPending && <Spinner />}

        {isSuccess && (
          <>
            <div className="rounded-md bg-green-50 border border-green-200 p-3 text-sm text-green-800">
              ¡Bienvenido/a! Ya eres parte de la natillera.
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
            >
              Ir al dashboard
            </button>
          </>
        )}

        {serverError && (
          <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
            {serverError}
          </div>
        )}
      </div>
    </div>
  );
}
