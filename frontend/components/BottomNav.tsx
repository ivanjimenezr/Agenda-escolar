import React from 'react';
import type { View } from '../types';
import { HomeIcon, CalendarIcon, UserIcon, MoonIcon } from './icons';

interface BottomNavProps {
  activeView: View;
  setActiveView: (view: View) => void;
}

const NavItem: React.FC<{
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}> = ({ icon, label, isActive, onClick }) => {
  const activeClasses = 'text-blue-600 dark:text-blue-400';
  const inactiveClasses = 'text-gray-400 dark:text-gray-500';

  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center justify-center w-full pt-2 pb-1 transition-all duration-200 active:scale-90"
    >
      <div className={`w-6 h-6 ${isActive ? activeClasses : inactiveClasses}`}>{icon}</div>
      <span className={`text-[10px] font-bold mt-1 uppercase tracking-tighter ${isActive ? activeClasses : inactiveClasses}`}>{label}</span>
    </button>
  );
};

const BottomNav: React.FC<BottomNavProps> = ({ activeView, setActiveView }) => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-18 pb-2 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 shadow-[0_-4px_10px_rgba(0,0,0,0.03)] flex justify-around items-center z-50">
      <NavItem
        icon={<HomeIcon />}
        label="Inicio"
        isActive={activeView === 'home'}
        onClick={() => setActiveView('home')}
      />
      <NavItem
        icon={<MoonIcon />}
        label="Cenas"
        isActive={activeView === 'dinners'}
        onClick={() => setActiveView('dinners')}
      />
      <NavItem
        icon={<CalendarIcon />}
        label="Gestionar"
        isActive={activeView === 'manage'}
        onClick={() => setActiveView('manage')}
      />
      <NavItem
        icon={<UserIcon />}
        label="Perfil"
        isActive={activeView === 'profile'}
        onClick={() => setActiveView('profile')}
      />
    </nav>
  );
};

export default BottomNav;