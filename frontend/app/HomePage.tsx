
import React, { useState } from 'react';
import type { StudentProfile, Subject, Exam, MenuItem, SchoolEvent, ActiveModules, DinnerItem, ModuleKey, Center, Contact, View } from '../types';
import { BookOpenIcon, CakeIcon, AcademicCapIcon, FlagIcon, MoonIcon, SparklesIcon, ChevronDownIcon, ChevronUpIcon, TrashIcon, PencilIcon, UserIcon, PlusIcon, PencilIcon as EditIcon } from '../components/icons';
import { aiService } from '../services/aiService';
import ItemFormModal from '../components/ItemFormModal';

interface HomePageProps {
  profile: StudentProfile;
  profiles: StudentProfile[];
  activeProfileId: string;
  setActiveProfileId: (id: string) => void;
  subjects: Subject[];
  exams: Exam[];
  menu: MenuItem[];
  events: SchoolEvent[];
  dinners: DinnerItem[];
  centers: Center[];
  contacts: Contact[];
  activeModules: ActiveModules;
  cardOrder: ModuleKey[];
  setCardOrder: (order: ModuleKey[]) => void;
  setDinners: (val: any) => void;
  setEvents: React.Dispatch<React.SetStateAction<SchoolEvent[]>>;
  setActiveView: (view: View) => void;
}

const today = new Date();
const todayISO = today.toISOString().split('T')[0];
const dayOfWeek = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'][today.getDay()];

const InfoCard: React.FC<{
    icon: React.ReactNode;
    title: string;
    children: React.ReactNode;
    index: number;
    isEditMode: boolean;
    onMoveUp?: () => void;
    onMoveDown?: () => void;
}> = ({ icon, title, children, index, isEditMode, onMoveUp, onMoveDown }) => (
    <div 
        className={`bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-4 mb-4 border border-gray-200 dark:border-gray-700 transition-all ${isEditMode ? 'ring-2 ring-blue-500/20 scale-[0.98]' : ''}`}
    >
        <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
                <div className="w-8 h-8 mr-3 flex items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                    {icon}
                </div>
                <h3 className="text-base font-bold text-gray-900 dark:text-gray-100">{title}</h3>
            </div>
            {isEditMode && (
                <div className="flex space-x-1">
                    <button onClick={onMoveUp} className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-500 active:bg-blue-100"><ChevronUpIcon className="w-4 h-4" /></button>
                    <button onClick={onMoveDown} className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-500 active:bg-blue-100"><ChevronDownIcon className="w-4 h-4" /></button>
                </div>
            )}
        </div>
        <div className="space-y-2">{children}</div>
    </div>
);

const HomePage: React.FC<HomePageProps> = ({ profile, profiles, activeProfileId, setActiveProfileId, subjects, exams, menu, events, dinners, centers, contacts, activeModules, cardOrder, setCardOrder, setDinners, setEvents, setActiveView }) => {
  const [isEditMode, setIsEditMode] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [isEventsExpanded, setIsEventsExpanded] = useState(false);
  const [editingEvent, setEditingEvent] = useState<SchoolEvent | null>(null);

  const moveCard = (index: number, direction: 'up' | 'down') => {
      const newOrder = [...cardOrder];
      const targetIndex = direction === 'up' ? index - 1 : index + 1;
      if (targetIndex < 0 || targetIndex >= newOrder.length) return;
      [newOrder[index], newOrder[targetIndex]] = [newOrder[targetIndex], newOrder[index]];
      setCardOrder(newOrder);
  };

  const handleQuickDinner = async () => {
    setGenerating(true);
    try {
        const menuToday = menu.find(m => m.date === todayISO);
        const result = await aiService.suggestDinner(
          menuToday?.mainCourse || 'comida variada',
          profile.allergies,
          profile.excludedFoods
        );
        if (result && result.meal) {
            const newDinner = { id: Date.now().toString(), date: todayISO, meal: result.meal, ingredients: [], studentId: activeProfileId };
            setDinners((prev: DinnerItem[]) => [...prev.filter(d => d.date !== todayISO), newDinner]);
        }
    } catch (e) { console.error(e); } finally { setGenerating(false); }
  };

  const todaysSubjects = subjects.filter(s => s.days.includes(dayOfWeek as any)).sort((a, b) => a.time.localeCompare(b.time));
  const todaysMenu = menu.find(m => m.date === todayISO);
  const todaysDinner = dinners.find(d => d.date === todayISO);
  const upcomingExams = exams.filter(e => new Date(e.date) >= new Date(today.setHours(0,0,0,0))).sort((a,b) => a.date.localeCompare(b.date)).slice(0, 2);
  const upcomingEvents = events.filter(e => new Date(e.date) >= new Date(new Date().setHours(0,0,0,0))).sort((a,b) => a.date.localeCompare(b.date));

  const deleteEvent = (id: string) => {
      if (confirm('¿Eliminar este evento?')) {
          setEvents(prev => prev.filter(e => e.id !== id));
      }
  };

  const renderModule = (key: ModuleKey, index: number) => {
      if (!activeModules[key]) return null;
      switch(key) {
          case 'subjects':
              return (
                <InfoCard key={key} icon={<BookOpenIcon />} title="Clases de Hoy" index={index} isEditMode={isEditMode} onMoveUp={() => moveCard(index, 'up')} onMoveDown={() => moveCard(index, 'down')}>
                    {todaysSubjects.length > 0 ? todaysSubjects.map(s => (
                        <div key={s.id} className="flex items-center p-3 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm">
                            <div className="w-1.5 h-10 rounded-full mr-3" style={{ backgroundColor: s.color || (s.type === 'extraescolar' ? '#a855f7' : '#3b82f6') }}></div>
                            <div className="flex-grow">
                                <div className="flex justify-between items-start">
                                    <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{s.name}</p>
                                    <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded-full border ${s.type === 'extraescolar' ? 'border-purple-200 text-purple-600 bg-purple-50 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800' : 'border-blue-200 text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800'}`}>
                                        {s.type === 'extraescolar' ? 'Extra' : 'Cole'}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{s.time} • {s.teacher}</p>
                            </div>
                        </div>
                    )) : <p className="text-center py-3 text-gray-400 dark:text-gray-500 text-sm font-medium italic">No hay clases hoy</p>}
                </InfoCard>
              );
          case 'contacts':
              return (
                <InfoCard key={key} icon={<UserIcon />} title="Directorio" index={index} isEditMode={isEditMode} onMoveUp={() => moveCard(index, 'up')} onMoveDown={() => moveCard(index, 'down')}>
                    <div className="space-y-3">
                        {centers.map(center => {
                            const centerContacts = contacts.filter(c => c.centerId === center.id);
                            if (centerContacts.length === 0) return null;
                            return (
                                <div key={center.id}>
                                    <p className="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1.5 ml-1">{center.name}</p>
                                    <div className="grid grid-cols-1 gap-1.5">
                                        {centerContacts.map(c => (
                                            <div key={c.id} className="p-3 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 flex justify-between items-center shadow-xs">
                                                <div>
                                                    <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{c.name}</p>
                                                    {c.role && <p className="text-[10px] text-gray-500 dark:text-gray-400">{c.role}</p>}
                                                </div>
                                                <a href={`tel:${c.phone}`} className="p-2 bg-blue-600 text-white rounded-lg active:scale-90 transition-transform shadow-sm">
                                                    <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/></svg>
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </InfoCard>
              );
          case 'menu':
              return (
                <InfoCard key={key} icon={<CakeIcon />} title="Menú Colegio" index={index} isEditMode={isEditMode} onMoveUp={() => moveCard(index, 'up')} onMoveDown={() => moveCard(index, 'down')}>
                    {todaysMenu ? (
                        <div className="p-3 rounded-xl bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-900/50 shadow-sm">
                            <p className="text-orange-900 dark:text-orange-200 font-bold text-sm leading-snug">{todaysMenu.mainCourse}</p>
                            <p className="text-orange-700/80 dark:text-orange-400/80 text-xs font-medium mt-1">{todaysMenu.sideDish} • {todaysMenu.dessert}</p>
                        </div>
                    ) : <p className="text-center py-3 text-gray-400 dark:text-gray-500 text-sm font-medium italic">Menú no disponible</p>}
                </InfoCard>
              );
          case 'dinner':
              return (
                <div 
                    key={key}
                    className={`bg-indigo-600 dark:bg-indigo-700 rounded-2xl shadow-md p-5 mb-4 text-white relative overflow-hidden transition-all ${isEditMode ? 'ring-2 ring-white/20 scale-[0.98]' : ''}`}
                >
                    <div className="flex items-center justify-between mb-4 relative z-10">
                        <div className="flex items-center">
                            <MoonIcon className="w-6 h-6 mr-2 text-indigo-200" />
                            <h3 className="text-base font-bold uppercase tracking-tight">Cena de Hoy</h3>
                        </div>
                        {isEditMode && (
                            <div className="flex space-x-1">
                                <button onClick={() => moveCard(index, 'up')} className="p-2 bg-white/10 rounded-lg text-white active:bg-white/20"><ChevronUpIcon className="w-4 h-4" /></button>
                                <button onClick={() => moveCard(index, 'down')} className="p-2 bg-white/10 rounded-lg text-white active:bg-white/20"><ChevronDownIcon className="w-4 h-4" /></button>
                            </div>
                        )}
                    </div>
                    {todaysDinner ? (
                        <div className="relative z-10">
                            <p className="text-lg font-bold leading-tight italic">"{todaysDinner.meal}"</p>
                            <div className="mt-3 flex items-center bg-white/10 w-fit px-3 py-1 rounded-full border border-white/10 text-[10px] font-bold tracking-wider">
                                <SparklesIcon className="w-3 h-3 mr-1" /> IA SUGERIDA
                            </div>
                        </div>
                    ) : (
                        <button 
                            onClick={handleQuickDinner} 
                            disabled={generating}
                            className="w-full py-3 bg-white text-indigo-600 rounded-xl font-bold text-sm shadow-lg active:scale-95 disabled:opacity-50"
                        >
                            {generating ? 'CONSULTANDO...' : 'SUGERIR CENA'}
                        </button>
                    )}
                </div>
              );
          case 'exams':
              return (
                <InfoCard key={key} icon={<AcademicCapIcon />} title="Próximos Exámenes" index={index} isEditMode={isEditMode} onMoveUp={() => moveCard(index, 'up')} onMoveDown={() => moveCard(index, 'down')}>
                    {upcomingExams.length > 0 ? upcomingExams.map(e => (
                        <div key={e.id} className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 flex justify-between items-center shadow-sm">
                            <div className="flex-1 mr-2">
                                <p className="font-bold text-red-950 dark:text-red-100 text-sm">{e.subject}</p>
                                <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide">{e.topic}</p>
                            </div>
                            <div className="text-right flex-shrink-0">
                                <p className="text-base font-bold leading-none text-red-900 dark:text-red-200">{new Date(e.date).getDate()}</p>
                                <p className="text-[9px] text-red-500/70 dark:text-red-400/70 font-bold uppercase">{new Date(e.date).toLocaleDateString('es-ES', { month: 'short' })}</p>
                            </div>
                        </div>
                    )) : <p className="text-center py-3 text-green-600 dark:text-green-400 text-sm font-bold">¡Sin exámenes pronto! 🎉</p>}
                </InfoCard>
              );
          default: return null;
      }
  };

  return (
    <div className="p-5 pb-24 dark:text-gray-100 animate-in fade-in duration-500 relative">
      
      {/* Perfil Switcher Superior */}
      <div className="mb-8 overflow-x-auto scrollbar-hide flex items-center space-x-4 py-2">
          {profiles.map(p => (
              <button 
                  key={p.id} 
                  onClick={() => setActiveProfileId(p.id)}
                  className={`flex-shrink-0 flex flex-col items-center transition-all ${activeProfileId === p.id ? 'scale-110 opacity-100' : 'scale-90 opacity-40'}`}
              >
                  <div className={`w-14 h-14 rounded-full p-1 border-2 mb-1 ${activeProfileId === p.id ? 'border-blue-500' : 'border-transparent'}`}>
                      <img src={p.avatarUrl} className="w-full h-full rounded-full object-cover bg-gray-100 dark:bg-gray-800" alt={p.name} />
                  </div>
                  <span className={`text-[10px] font-bold ${activeProfileId === p.id ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'}`}>{p.name.split(' ')[0]}</span>
              </button>
          ))}
          <button className="flex-shrink-0 flex flex-col items-center opacity-30 hover:opacity-100 transition-opacity" onClick={() => setActiveView('profile')}>
              <div className="w-14 h-14 rounded-full border-2 border-dashed border-gray-400 dark:border-gray-600 flex items-center justify-center mb-1">
                  <PlusIcon className="w-6 h-6 text-gray-400" />
              </div>
              <span className="text-[10px] font-bold text-gray-400">Añadir</span>
          </button>
      </div>

      <header className="mb-6 flex justify-between items-end">
        <div>
            <p className="text-blue-600 dark:text-blue-400 font-bold text-xs uppercase tracking-wider mb-1">{dayOfWeek}, {today.getDate()} de {today.toLocaleDateString('es-ES', { month: 'long' })}</p>
            <h1 className="text-2xl font-black text-gray-900 dark:text-white leading-tight">Agenda de<br/>{profile.name}</h1>
        </div>
        <button 
            onClick={() => setIsEditMode(!isEditMode)}
            className={`p-3 rounded-xl border transition-all ${isEditMode ? 'bg-blue-600 text-white border-blue-600 shadow-lg' : 'bg-white dark:bg-gray-800 text-gray-500 border-gray-200 dark:border-gray-700'}`}
        >
            <EditIcon className="w-5 h-5" />
        </button>
      </header>

      {activeModules.events && upcomingEvents.length > 0 && (
          <div className="mb-6 overflow-hidden transition-all duration-300">
              <button onClick={() => setIsEventsExpanded(!isEventsExpanded)} className={`w-full p-4 rounded-2xl flex items-center justify-between shadow-sm transition-all ${isEventsExpanded ? 'bg-amber-500 text-white rounded-b-none shadow-lg' : 'bg-amber-400 text-amber-950 border border-amber-500/20'}`}>
                  <div className="flex items-center">
                    <FlagIcon className={`w-5 h-5 mr-3 ${isEventsExpanded ? 'text-white' : 'text-amber-800'}`} />
                    <p className="font-bold text-sm">{isEventsExpanded ? 'Calendario de Eventos' : `Tienes ${upcomingEvents.length} eventos próximos`}</p>
                  </div>
                  {isEventsExpanded ? <ChevronUpIcon className="w-5 h-5" /> : <ChevronDownIcon className="w-5 h-5" />}
              </button>
              {isEventsExpanded && (
                  <div className="bg-amber-50 dark:bg-gray-800 border-x border-b border-amber-200 dark:border-gray-700 rounded-b-2xl p-3 space-y-2 animate-in slide-in-from-top-1">
                      {upcomingEvents.map(ev => (
                          <div key={ev.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-xl shadow-xs border border-amber-100 dark:border-gray-700">
                              <div className="flex-grow">
                                  <p className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-tight">{new Date(ev.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}</p>
                                  <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{ev.name}</p>
                              </div>
                              <div className="flex items-center space-x-1">
                                  <button onClick={() => setEditingEvent(ev)} className="p-2 text-blue-500 bg-blue-50 dark:bg-blue-900/20 rounded-lg"><PencilIcon className="w-3 h-3" /></button>
                                  <button onClick={() => deleteEvent(ev.id)} className="p-2 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg"><TrashIcon className="w-3 h-3" /></button>
                              </div>
                          </div>
                      ))}
                  </div>
              )}
          </div>
      )}

      <main>{cardOrder.filter(k => activeModules[k]).map((key, index) => renderModule(key, index))}</main>
      
      {isEditMode && (
          <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[100] animate-in slide-in-from-bottom duration-300">
              <button 
                onClick={() => setIsEditMode(false)}
                className="px-6 py-3 bg-blue-600 text-white rounded-full font-black text-xs uppercase tracking-widest shadow-2xl border-2 border-white dark:border-gray-800"
              >
                Finalizar Orden
              </button>
          </div>
      )}

      {editingEvent && <ItemFormModal item={editingEvent} type="events" title="Evento" onClose={() => setEditingEvent(null)} onSave={(data) => { setEvents(prev => prev.map(e => e.id === editingEvent.id ? { ...e, ...data } : e)); setEditingEvent(null); }} />}
    </div>
  );
};
export default HomePage;
