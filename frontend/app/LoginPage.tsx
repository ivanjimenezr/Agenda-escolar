
import React, { useState, useEffect } from 'react';
import type { User } from '../types';
import { SparklesIcon, EyeIcon, EyeOffIcon } from '../components/icons';
import { login, register } from '../services/authService';
import {
  isLockedOut,
  recordAttempt,
  getSecurityInfo,
  type SecurityInfo
} from '../utils/bruteForceProtection';
import { validatePassword, type PasswordValidation } from '../utils/passwordValidation';

interface LoginPageProps {
  onLogin: (user: User) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [securityInfo, setSecurityInfo] = useState<SecurityInfo | null>(null);
  const [countdown, setCountdown] = useState(0);
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  // Update security info when email changes
  useEffect(() => {
    if (email && mode === 'login') {
      const info = getSecurityInfo(email);
      setSecurityInfo(info);
      setCountdown(info.lockoutTimeRemaining);
    } else {
      setSecurityInfo(null);
      setCountdown(0);
    }
  }, [email, mode]);

  // Countdown timer for lockout
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
        // Refresh security info when countdown reaches 0
        if (countdown === 1 && email) {
          const info = getSecurityInfo(email);
          setSecurityInfo(info);
        }
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown, email]);

  // Validate password in real-time (only in register mode)
  useEffect(() => {
    if (mode === 'register' && password) {
      const validation = validatePassword(password);
      setPasswordValidation(validation);
    } else {
      setPasswordValidation(null);
    }
  }, [password, mode]);

  // Reset password visibility when switching modes
  useEffect(() => {
    setShowPassword(false);
  }, [mode]);

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password.trim() || (mode === 'register' && !name.trim())) {
      setError('Por favor, completa todos los campos.');
      return;
    }

    if (!validateEmail(email)) {
      setError('El formato del correo electrónico no es válido.');
      return;
    }

    // Validate password strength (only for register mode)
    if (mode === 'register') {
      const validation = validatePassword(password);
      if (!validation.isValid) {
        setError('La contraseña no cumple con todos los requisitos.');
        return;
      }
    } else {
      // For login, just check minimum length
      if (password.length < 8) {
        setError('La contraseña debe tener al menos 8 caracteres.');
        return;
      }
    }

    // Check brute force protection (only for login mode)
    if (mode === 'login') {
      const lockout = isLockedOut(email);
      if (lockout) {
        setError(`Cuenta bloqueada temporalmente. Intenta de nuevo en ${Math.ceil(countdown / 60)} minutos.`);
        return;
      }

      const info = getSecurityInfo(email);
      if (info.shouldWait) {
        setError(`Demasiados intentos. Espera ${Math.ceil(info.attemptDelay / 1000)} segundos antes de intentar de nuevo.`);
        return;
      }
    }

    setLoading(true);

    try {
      if (mode === 'register') {
        // Register new user via backend API
        const user = await register({ name, email, password });
        // After registration, automatically log in
        const loginUser = await login({ email, password });
        recordAttempt(email, true); // Record successful login
        onLogin({ name: loginUser.name, email: loginUser.email });
      } else {
        // Login existing user via backend API
        const user = await login({ email, password });
        recordAttempt(email, true); // Record successful login
        onLogin({ name: user.name, email: user.email });
      }
    } catch (err: any) {
      // Record failed attempt only for login mode
      if (mode === 'login') {
        recordAttempt(email, false);
        const info = getSecurityInfo(email);
        setSecurityInfo(info);
        setCountdown(info.lockoutTimeRemaining);
      }
      setError(err.message || 'Ocurrió un error. Por favor, intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (val: string, isEmail: boolean = false) => `
    w-full p-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-2xl border 
    ${error && !val ? 'border-red-500' : (isEmail && val && !validateEmail(val) ? 'border-orange-500' : 'border-gray-200 dark:border-gray-700')}
    text-sm font-semibold shadow-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all
  `;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 dark:from-gray-950 dark:to-gray-900">
      <div className="w-full max-w-md space-y-8 animate-in fade-in zoom-in duration-500">
        <div className="text-center text-white">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-xl rounded-[2.2rem] shadow-2xl mb-6 border border-white/30">
            <SparklesIcon className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-black tracking-tight">{mode === 'login' ? 'Bienvenido de nuevo' : 'Crea tu cuenta'}</h1>
          <p className="text-blue-100/80 mt-2 font-medium">Gestiona el futuro escolar hoy</p>
        </div>

        <div className="bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl p-8 rounded-[2.5rem] shadow-2xl border border-white/20 space-y-6">
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-xs font-bold rounded-xl text-center border border-red-100 dark:border-red-800 animate-shake">
              {error}
            </div>
          )}

          {/* Security Warning - Lockout */}
          {mode === 'login' && securityInfo?.isLocked && (
            <div className="p-4 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400 text-xs font-bold rounded-xl border border-orange-200 dark:border-orange-800">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
                <span>Cuenta Bloqueada Temporalmente</span>
              </div>
              <p className="text-[10px]">
                Demasiados intentos fallidos. Podrás intentar de nuevo en{' '}
                <span className="font-black text-orange-600 dark:text-orange-300">
                  {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, '0')}
                </span>
              </p>
            </div>
          )}

          {/* Security Info - Remaining Attempts */}
          {mode === 'login' && securityInfo && !securityInfo.isLocked && securityInfo.remainingAttempts < 5 && email && (
            <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 text-xs font-bold rounded-xl border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center justify-between">
                <span>⚠️ Intentos restantes:</span>
                <span className="text-lg font-black">{securityInfo.remainingAttempts}</span>
              </div>
            </div>
          )}

          <form onSubmit={handleAuth} className="space-y-4">
            {mode === 'register' && (
              <div className="animate-in slide-in-from-top-2 duration-300">
                <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Nombre Completo</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={e => setName(e.target.value)}
                  className={inputClass(name)}
                  placeholder="Ej: Juan Pérez"
                />
              </div>
            )}

            <div>
              <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Correo Electrónico</label>
              <input 
                type="text" 
                value={email} 
                onChange={e => setEmail(e.target.value)}
                className={inputClass(email, true)}
                placeholder="tu@email.com"
              />
              {email && !validateEmail(email) && (
                <p className="text-[9px] text-orange-500 font-bold mt-1 ml-1 uppercase">Formato de email no válido</p>
              )}
            </div>

            <div>
              <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Contraseña</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className={inputClass(password)}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors focus:outline-none"
                  aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showPassword ? (
                    <EyeOffIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>

              {/* Password Requirements Indicator (only in register mode) */}
              {mode === 'register' && password && passwordValidation && (
                <div className="mt-3 space-y-1.5 animate-in fade-in slide-in-from-top-1 duration-300">
                  {passwordValidation.requirements.map((req) => (
                    <div
                      key={req.id}
                      className={`flex items-center gap-2 text-[10px] font-bold transition-all duration-300 ${
                        req.met
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-500 dark:text-red-400'
                      }`}
                    >
                      <span
                        className={`flex items-center justify-center w-4 h-4 rounded-full transition-all duration-300 ${
                          req.met
                            ? 'bg-green-100 dark:bg-green-900/30'
                            : 'bg-red-100 dark:bg-red-900/30'
                        }`}
                      >
                        {req.met ? (
                          <svg
                            className="w-3 h-3"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="w-3 h-3"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </span>
                      <span className="uppercase tracking-wide">{req.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || (mode === 'login' && securityInfo?.isLocked)}
              className="w-full py-4 bg-blue-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl shadow-blue-600/30 active:scale-95 transition-all mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cargando...' :
               (mode === 'login' && securityInfo?.isLocked) ? '🔒 Bloqueado' :
               (mode === 'login' ? 'Iniciar Sesión' : 'Registrarme')}
            </button>
          </form>

          <div className="pt-4 border-t border-gray-100 dark:border-gray-800 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400 font-bold mb-3">
              {mode === 'login' ? '¿No tienes cuenta?' : '¿Ya eres usuario?'}
            </p>
            <button 
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
              className="text-blue-600 dark:text-blue-400 text-xs font-black uppercase tracking-widest hover:underline"
            >
              {mode === 'login' ? 'Crea una cuenta ahora' : 'Inicia sesión aquí'}
            </button>
          </div>
        </div>

        <p className="text-center text-[10px] text-white/50 font-bold uppercase tracking-widest">
          Desarrollado para Control Escolar Pro
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
