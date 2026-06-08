import { useEffect } from 'react';

const TYPE_STYLES = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  info: 'bg-blue-600',
  warning: 'bg-yellow-500',
};

export default function Toast({ message, type = 'info', onClose, duration = 4000 }) {
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(onClose, duration);
    return () => clearTimeout(t);
  }, [message, duration, onClose]);

  if (!message) return null;

  return (
    <div className={`fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg text-white shadow-lg ${TYPE_STYLES[type]} min-w-[240px] max-w-sm`}>
      <span className="flex-1 text-sm">{message}</span>
      <button onClick={onClose} className="text-white/80 hover:text-white text-lg leading-none">&times;</button>
    </div>
  );
}
