import { describe, it, expect } from 'vitest';
import { formatCOP } from '../formatCurrency';

describe('formatCOP', () => {
  it('formats zero as $ 0', () => {
    const result = formatCOP(0);
    expect(result.replace(/\s/g, ' ')).toBe('$ 0');
  });

  it('formats positive numbers', () => {
    const result = formatCOP(1250000);
    expect(result.replace(/\s/g, '')).toContain('1.250.000');
  });

  it('formats negative numbers', () => {
    const result = formatCOP(-50000);
    expect(result.replace(/\s/g, '')).toContain('50.000');
  });

  it('formats string numbers', () => {
    const result = formatCOP('100000');
    expect(result.replace(/\s/g, '')).toContain('100.000');
  });

  it('returns $ 0 for NaN', () => {
    const result = formatCOP('invalid');
    expect(result.replace(/\s/g, ' ')).toBe('$ 0');
  });

  it('formats large numbers correctly', () => {
    const result = formatCOP(10000000);
    expect(result.replace(/\s/g, '')).toContain('10.000.000');
  });

  it('formats small amounts', () => {
    const result = formatCOP(500);
    expect(result.replace(/\s/g, '')).toContain('500');
  });
});
