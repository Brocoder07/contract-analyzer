import { useMemo, useState } from 'react';
import type { AuthUser, LoginRequest, RegisterRequest } from '../types';
import { contractAnalysisAPI } from '../services/api';
import './AuthPanel.css';

interface AuthPanelProps {
  user: AuthUser | null;
  loadingSession?: boolean;
  onLoginSuccess: (token: string, user: AuthUser) => void;
  onLogout: () => void;
}

type Mode = 'login' | 'register';

export function AuthPanel({ user, loadingSession = false, onLoginSuccess, onLogout }: AuthPanelProps) {
  const [mode, setMode] = useState<Mode>('login');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [loginForm, setLoginForm] = useState<LoginRequest>({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState<RegisterRequest>({
    email: '',
    full_name: '',
    password: '',
  });

  const title = useMemo(() => (mode === 'login' ? 'Sign in' : 'Create account'), [mode]);

  const submitLogin = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await contractAnalysisAPI.login(loginForm);
      onLoginSuccess(result.access_token, result.user);
      setSuccess('Logged in successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitRegister = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      await contractAnalysisAPI.register(registerForm);
      setSuccess('Registration successful. Please log in.');
      setMode('login');
      setLoginForm((prev) => ({ ...prev, email: registerForm.email }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loadingSession) {
    return (
      <section className="auth-panel">
        <p className="auth-muted">Checking session…</p>
      </section>
    );
  }

  if (user) {
    return (
      <section className="auth-panel auth-panel-logged-in">
        <div>
          <h3>Signed in</h3>
          <p className="auth-muted">
            {user.full_name} · {user.email}
          </p>
        </div>
        <button className="auth-btn auth-btn-secondary" onClick={onLogout}>
          Logout
        </button>
      </section>
    );
  }

  return (
    <section className="auth-panel">
      <div className="auth-panel-top">
        <h3>{title}</h3>
        <div className="auth-mode-switch">
          <button
            className={`auth-mode-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
            type="button"
          >
            Login
          </button>
          <button
            className={`auth-mode-btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
            type="button"
          >
            Register
          </button>
        </div>
      </div>

      {error && <p className="auth-alert auth-alert-error">{error}</p>}
      {success && <p className="auth-alert auth-alert-success">{success}</p>}

      {mode === 'login' ? (
        <form
          className="auth-form"
          onSubmit={(e) => {
            e.preventDefault();
            void submitLogin();
          }}
        >
          <input
            className="auth-input"
            type="email"
            placeholder="Email"
            value={loginForm.email}
            onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
          <input
            className="auth-input"
            type="password"
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
            required
          />
          <button className="auth-btn auth-btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      ) : (
        <form
          className="auth-form"
          onSubmit={(e) => {
            e.preventDefault();
            void submitRegister();
          }}
        >
          <input
            className="auth-input"
            type="text"
            placeholder="Full name"
            value={registerForm.full_name}
            onChange={(e) => setRegisterForm((prev) => ({ ...prev, full_name: e.target.value }))}
            required
          />
          <input
            className="auth-input"
            type="email"
            placeholder="Email"
            value={registerForm.email}
            onChange={(e) => setRegisterForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
          <input
            className="auth-input"
            type="password"
            placeholder="Password (min 8 chars)"
            value={registerForm.password}
            onChange={(e) => setRegisterForm((prev) => ({ ...prev, password: e.target.value }))}
            minLength={8}
            required
          />
          <button className="auth-btn auth-btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
      )}
    </section>
  );
}
