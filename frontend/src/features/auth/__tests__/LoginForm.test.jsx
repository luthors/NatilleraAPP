import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginForm from '../components/LoginForm';

vi.mock('../../store/authStore', () => ({
  useAuthStore: vi.fn(() => ({ usuario: null })),
}));

vi.mock('../hooks/useLogin', () => ({
  useLogin: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    error: null,
  })),
}));

const renderWithRouter = (component) => {
  return render(<MemoryRouter>{component}</MemoryRouter>);
};

describe('LoginForm', () => {
  it('renders email and password inputs', () => {
    renderWithRouter(<LoginForm />);
    expect(screen.getByPlaceholderText('tucorreo@ejemplo.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    renderWithRouter(<LoginForm />);
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('renders link to register page', () => {
    renderWithRouter(<LoginForm />);
    expect(screen.getByText(/regístrate/i)).toBeInTheDocument();
  });

  it('renders link to forgot password', () => {
    renderWithRouter(<LoginForm />);
    expect(screen.getByText(/olvidaste tu contraseña/i)).toBeInTheDocument();
  });

  it('updates form values on input change', () => {
    renderWithRouter(<LoginForm />);
    const emailInput = screen.getByPlaceholderText('tucorreo@ejemplo.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Passw0rd!' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('Passw0rd!');
  });
});
