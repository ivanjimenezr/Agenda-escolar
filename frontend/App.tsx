
import React, { useState, useMemo, useEffect } from 'react';
import type { View, StudentProfile, Subject, Exam, MenuItem, SchoolEvent, ActiveModules, DinnerItem, ModuleKey, Center, Contact, User } from './types';
import useLocalStorage from './hooks/useLocalStorage';
import BottomNav from './components/BottomNav';
import HomePage from './app/HomePage';
import ManagePage from './app/ManagePage';
import ProfilePage from './app/ProfilePage';
import DinnersPage from './app/DinnersPage';
import LoginPage from './app/LoginPage';

const initialId = 'default-child-1';

const defaultActiveModules: ActiveModules = {
  subjects: true,
  exams: true,
  menu: true,
  events: true,
  dinner: true,
  contacts: true,
};

const defaultProfile: StudentProfile = {
  id: initialId,
  name: 'Alex García',
  school: 'Colegio Cervantes',
  grade: '5º de Primaria',
  avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=Alex`,
  allergies: [],
  excludedFoods: [],
  activeModules: defaultActiveModules
};

const subjectsMock: Subject[] = [
    { id: '1', studentId: initialId, name: 'Matemáticas', days: ['Lunes', 'Miércoles'], time: '09:00', teacher: 'Sra. Pérez', color: '#3b82f6', type: 'colegio' },
    { id: '2', studentId: initialId, name: 'Judo', days: ['Lunes', 'Viernes'], time: '17:30', teacher: 'Sensei Ryu', color: '#a855f7', type: 'extraescolar' },
];

const defaultCardOrder: ModuleKey[] = ['subjects', 'menu', 'dinner', 'exams', 'contacts'];

const App: React.FC = () => {
  const [user, setUser] = useLocalStorage<User | null>('school-agenda-auth-v2', null);
  const [activeView, setActiveView] = useState<View>('home');
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('school-agenda-theme', 'light');
  
  const [profiles, setProfiles] = useLocalStorage<StudentProfile[]>('school-agenda-profiles', [defaultProfile]);
  const [activeProfileId, setActiveProfileId] = useLocalStorage<string>('school-agenda-active-id', initialId);
  
  const [allSubjects, setAllSubjects] = useLocalStorage<Subject[]>('school-agenda-subjects', subjectsMock);
  const [allExams, setAllExams] = useLocalStorage<Exam[]>('school-agenda-exams', []);
  const [allDinners, setAllDinners] = useLocalStorage<DinnerItem[]>('school-agenda-dinners', []);
  
  const [menu, setMenu] = useLocalStorage<MenuItem[]>('school-agenda-menu', []);
  const [events, setEvents] = useLocalStorage<SchoolEvent[]>('school-agenda-events', []);
  const [centers, setCenters] = useLocalStorage<Center[]>('school-agenda-centers', [{ id: '1', name: 'Colegio Cervantes' }]);
  const [contacts, setContacts] = useLocalStorage<Contact[]>('school-agenda-contacts', []);
  
  const [cardOrder, setCardOrder] = useLocalStorage<ModuleKey[]>('school-agenda-order', defaultCardOrder);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const activeProfile = useMemo(() => 
    profiles.find(p => p.id === activeProfileId) || profiles[0], 
    [profiles, activeProfileId]
  );

  const activeModules = activeProfile?.activeModules || defaultActiveModules;

  const subjects = useMemo(() => allSubjects.filter(s => s.studentId === activeProfileId), [allSubjects, activeProfileId]);
  const exams = useMemo(() => allExams.filter(e => e.studentId === activeProfileId), [allExams, activeProfileId]);
  const dinners = useMemo(() => allDinners.filter(d => d.studentId === activeProfileId), [allDinners, activeProfileId]);

  if (!user) {
    return <LoginPage onLogin={setUser} />;
  }

  const renderContent = () => {
    if (!activeProfile) return <div className="p-10 text-center dark:text-gray-400 font-bold">Iniciando sesión...</div>;

    switch(activeView) {
      case 'home':
        return <HomePage 
                  profile={activeProfile} 
                  profiles={profiles}
                  activeProfileId={activeProfileId}
                  setActiveProfileId={setActiveProfileId}
                  subjects={subjects} 
                  exams={exams} 
                  menu={menu} 
                  events={events} 
                  dinners={dinners}
                  centers={centers}
                  contacts={contacts}
                  activeModules={activeModules} 
                  cardOrder={cardOrder}
                  setCardOrder={setCardOrder}
                  setDinners={(val) => {
                      if (typeof val === 'function') {
                          setAllDinners(prev => {
                              const currentChildDinners = prev.filter(d => d.studentId === activeProfileId);
                              const otherChildDinners = prev.filter(d => d.studentId !== activeProfileId);
                              const updated = val(currentChildDinners);
                              return [...otherChildDinners, ...updated.map(d => ({...d, studentId: activeProfileId}))];
                          });
                      }
                  }}
                  setEvents={setEvents}
                  setActiveView={setActiveView}
                />;
      case 'dinners':
        return <DinnersPage 
                  dinners={dinners} 
                  setDinners={(val) => {
                    if (typeof val === 'function') {
                        setAllDinners(prev => {
                            const currentChildDinners = prev.filter(d => d.studentId === activeProfileId);
                            const otherChildDinners = prev.filter(d => d.studentId !== activeProfileId);
                            const updated = val(currentChildDinners);
                            return [...otherChildDinners, ...updated.map(d => ({...d, studentId: activeProfileId}))];
                        });
                    }
                  }} 
                  menu={menu} 
                  profile={activeProfile}
                />;
      case 'manage':
        return <ManagePage 
                  activeProfileId={activeProfileId}
                  subjects={subjects} 
                  setSubjects={(val) => {
                      if (typeof val === 'function') {
                          setAllSubjects(prev => {
                              const other = prev.filter(s => s.studentId !== activeProfileId);
                              const current = prev.filter(s => s.studentId === activeProfileId);
                              const updated = val(current);
                              return [...other, ...updated.map(s => ({...s, studentId: activeProfileId}))];
                          });
                      }
                  }}
                  exams={exams} 
                  setExams={(val) => {
                    if (typeof val === 'function') {
                        setAllExams(prev => {
                            const other = prev.filter(e => e.studentId !== activeProfileId);
                            const current = prev.filter(e => e.studentId === activeProfileId);
                            const updated = val(current);
                            return [...other, ...updated.map(e => ({...e, studentId: activeProfileId}))];
                        });
                    }
                  }}
                  menu={menu} setMenu={setMenu}
                  events={events} setEvents={setEvents}
                  centers={centers} setCenters={setCenters}
                  contacts={contacts} setContacts={setContacts}
                  activeModules={activeModules}
                />;
      case 'profile':
        return <ProfilePage 
                  profile={activeProfile} 
                  profiles={profiles}
                  setProfiles={setProfiles}
                  setProfile={(updated) => {
                      setProfiles(prev => prev.map(p => p.id === activeProfileId ? (typeof updated === 'function' ? updated(p) : updated) : p));
                  }}
                  activeProfileId={activeProfileId}
                  setActiveProfileId={setActiveProfileId}
                  activeModules={activeModules} 
                  setActiveModules={(val) => {
                      setProfiles(prev => prev.map(p => {
                          if (p.id === activeProfileId) {
                              const nextModules = typeof val === 'function' ? val(p.activeModules) : val;
                              return { ...p, activeModules: nextModules };
                          }
                          return p;
                      }));
                  }} 
                  theme={theme}
                  setTheme={setTheme}
                  onLogout={() => { if(confirm('¿Deseas cerrar sesión en este dispositivo?')) setUser(null); }}
                />;
      default:
        return null;
    }
  }

  return (
    <div className="h-screen w-screen font-sans bg-gray-50 dark:bg-gray-950 overflow-hidden transition-colors duration-300">
      <div className="container mx-auto max-w-lg h-full flex flex-col shadow-2xl bg-white dark:bg-gray-900 border-x border-gray-100 dark:border-gray-800 transition-colors duration-300">
        <main className="flex-grow overflow-y-auto scrollbar-hide">
          {renderContent()}
        </main>
        {user && <BottomNav activeView={activeView} setActiveView={setActiveView} />}
      </div>
    </div>
  );
}

export default App;
