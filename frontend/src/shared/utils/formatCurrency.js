/**
 * formatCurrency — Formats a number as Colombian Peso (COP).
 *
 * @param {number|string} value - Amount in pesos (not cents).
 * @returns {string} Formatted string, e.g. "$ 1.250.000"
 */
const _formatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function formatCOP(value) {
  const num = Number(value);
  if (isNaN(num)) return '$ 0';
  return _formatter.format(num);
}

export default formatCOP;
