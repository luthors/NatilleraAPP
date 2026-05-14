import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import AppLayout from '../shared/components/AppLayout';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/apiClient';

export default function PerfilPage() {
  const { usuario, setUsuario } = useAuthStore();
  const queryClient = useQueryClient();

  const [form, setForm] = useState({
    nombre: usuario?.nombre || '',
    telefono: usuario?.telefono || '',
  });
  const [toast, setToast] = useState('');

  const { mutate: actualizar, isPending, error } = useMutation({
    mutationFn: async (datos) => {
      const { data } = await apiClient.patch('/usuarios/me', datos);
      return data;
    },
    onSuccess: (data) => {
      setUsuario(data);
      queryClient.invalidateQueries({ queryKey: ['usuario-me'] });
      setToast('Perfil actualizado');
      setTimeout(() => setToast(''), 3000);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const updates = {};
    if (form.nombre !== usuario?.nombre) updates.nombre = form.nombre;
    if (form.telefono !== (usuario?.telefono || '')) updates.telefono = form.telefono || null;
    if (Object.keys(updates).length > 0) actualizar(updates);
  };

  const serverError = error?.response?.data?.detail || error?.message;

  return (
    <AppLayout>
      {toast && (
        <div className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white text-sm px-4 py-3 rounded-lg shadow-lg">
          {toast}
        </div>
      )}

      <div className="max-w-md">
        <h1 className="text-xl font-bold text-gray-900 mb-6">Mi perfil</h1>

        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
          {/* Avatar placeholder */}
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center text-2xl text-primary font-bold select-none">
              {usuario?.nombre?.[0]?.toUpperCase() || '?'}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{usuario?.nombre}</p>
              <p className="text-sm text-gray-500">{usuario?.email}</p>
            </div>
          </div>

          {serverError && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
              <input
                type="text"
                value={form.nombre}
                onChange={(e) => setForm((p) => ({ ...p, nombre: e.target.value }))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input
                type="tel"
                value={form.telefono}
                onChange={(e) => setForm((p) => ({ ...p, telefono: e.target.value }))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="+57 300 000 0000"
              />
            </div>
            <button
              type="submit"
              disabled={isPending}
              className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              {isPending ? 'Guardando…' : 'Guardar cambios'}
            </button>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}
