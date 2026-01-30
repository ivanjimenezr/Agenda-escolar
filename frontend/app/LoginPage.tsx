
import React, { useState } from 'react';
import type { User } from '../types';
import { SparklesIcon } from '../components/icons';
import { login, register } from '../services/authService';

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

    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }

    setLoading(true);

    try {
      if (mode === 'register') {
        // Register new user via backend API
        const user = await register({ name, email, password });
        // After registration, automatically log in
        const loginUser = await login({ email, password });
        onLogin({ name: loginUser.name, email: loginUser.email });
      } else {
        // Login existing user via backend API
        const user = await login({ email, password });
        onLogin({ name: user.name, email: user.email });
      }
    } catch (err: any) {
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
              <input 
                type="password" 
                value={password} 
                onChange={e => setPassword(e.target.value)}
                className={inputClass(password)}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-blue-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl shadow-blue-600/30 active:scale-95 transition-all mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cargando...' : (mode === 'login' ? 'Iniciar Sesión' : 'Registrarme')}
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
