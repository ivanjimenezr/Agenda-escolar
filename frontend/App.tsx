
import React, { useState, useMemo, useEffect } from 'react';
import type { View, StudentProfile, Subject, Exam, MenuItem, SchoolEvent, ActiveModules, DinnerItem, ModuleKey, Center, Contact, User } from './types';
import useLocalStorage from './hooks/useLocalStorage';
import BottomNav from './components/BottomNav';
import HomePage from './app/HomePage';
import ManagePage from './app/ManagePage';
import ProfilePage from './app/ProfilePage';
import DinnersPage from './app/DinnersPage';
import LoginPage from './app/LoginPage';
import { getMyStudents } from './services/studentService';
import { getStudentMenus } from './services/menuService';
import { getActiveModules } from './services/activeModulesService';
import { transformStudent, transformMenu } from './utils/dataTransformers';

const defaultActiveModules: ActiveModules = {
  subjects: true,
  exams: true,
  menu: true,
  events: true,
  dinner: true,
  contacts: true,
};

const defaultCardOrder: ModuleKey[] = ['subjects', 'menu', 'dinner', 'exams', 'contacts'];

const App: React.FC = () => {
  const [user, setUser] = useLocalStorage<User | null>('school-agenda-auth-v2', null);
  const [activeView, setActiveView] = useState<View>('home');
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('school-agenda-theme', 'light');
  
  const [profiles, setProfiles] = useState<StudentProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useLocalStorage<string>('school-agenda-active-id', '');
  const [loading, setLoading] = useState(true);

  const [allSubjects, setAllSubjects] = useLocalStorage<Subject[]>('school-agenda-subjects', []);
  const [allExams, setAllExams] = useLocalStorage<Exam[]>('school-agenda-exams', []);
  const [allDinners, setAllDinners] = useLocalStorage<DinnerItem[]>('school-agenda-dinners', []);

  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [events, setEvents] = useLocalStorage<SchoolEvent[]>('school-agenda-events', []);
  const [centers, setCenters] = useLocalStorage<Center[]>('school-agenda-centers', []);
  const [contacts, setContacts] = useLocalStorage<Contact[]>('school-agenda-contacts', []);

  const [cardOrder, setCardOrder] = useLocalStorage<ModuleKey[]>('school-agenda-order', defaultCardOrder);

  // Load students from backend when user logs in
  useEffect(() => {
    if (user) {
      loadStudents();
    }
  }, [user]);

  // Load menus when active profile changes
  useEffect(() => {
    if (activeProfileId) {
      loadMenus(activeProfileId);
    }
  }, [activeProfileId]);

  // Theme effect
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const students = await getMyStudents();

      // Load active modules for each student
      const transformedStudents = await Promise.all(
        students.map(async (student) => {
          try {
            const activeModulesData = await getActiveModules(student.id);
            // Transform backend active_modules to frontend format
            const activeModules = {
              subjects: activeModulesData.subjects,
              exams: activeModulesData.exams,
              menu: activeModulesData.menu,
              events: activeModulesData.events,
              dinner: activeModulesData.dinner,
              contacts: activeModulesData.contacts,
            };
            return transformStudent(student, activeModules);
          } catch (error) {
            console.error(`Error loading active modules for student ${student.id}:`, error);
            // If fails to load active modules, use defaults
            return transformStudent(student);
          }
        })
      );

      setProfiles(transformedStudents);

      // Set active profile to first student if none selected
      if (!activeProfileId && transformedStudents.length > 0) {
        setActiveProfileId(transformedStudents[0].id);
      }
    } catch (error: any) {
      console.error('[App] Error loading students:', error);
      // If it's a 401, the apiClient will handle logout automatically
      // For other errors, we might want to show a message or logout
      if (error?.status === 401 || error?.message?.includes('Unauthorized')) {
        console.log('[App] Session expired, user will be logged out automatically');
      } else {
        console.error('[App] Unexpected error loading students:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMenus = async (studentId: string) => {
    try {
      console.log('[App] Loading menus for student:', studentId);
      const menus = await getStudentMenus(studentId);
      console.log('[App] Received menus from API:', menus);
      const transformedMenus = menus.map(transformMenu);
      console.log('[App] Transformed menus:', transformedMenus);
      setMenu(transformedMenus);
    } catch (error) {
      console.error('[App] Error loading menus:', error);
    }
  };

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
    if (loading) {
      return (
        <div className="p-10 text-center dark:text-gray-400">
          <div className="mb-4 text-6xl animate-pulse">⏳</div>
          <h2 className="text-xl font-black mb-2 dark:text-white">Cargando...</h2>
          <p className="text-sm font-semibold">Obteniendo tus datos</p>
        </div>
      );
    }

    // Si no hay perfiles pero el usuario quiere ir a la vista de profile, permitirlo
    if (!activeProfile && activeView !== 'profile') {
      return (
        <div className="p-10 text-center dark:text-gray-400">
          <div className="mb-4 text-6xl">👤</div>
          <h2 className="text-xl font-black mb-2 dark:text-white">Bienvenido a Agenda Escolar Pro</h2>
          <p className="text-sm font-semibold mb-6">No tienes ningún perfil de estudiante configurado.</p>
          <button
            onClick={() => {
              console.log('Botón "Crear Primer Perfil" clickeado');
              console.log('Cambiando vista a: profile');
              setActiveView('profile');
            }}
            className="px-6 py-3 bg-blue-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl hover:bg-blue-700 active:scale-95 transition-all"
          >
            Crear Primer Perfil
          </button>
        </div>
      );
    }

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
                  reloadMenus={() => loadMenus(activeProfileId)}
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
                  reloadStudents={loadStudents}
                  user={user}
                  setUser={setUser}
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
