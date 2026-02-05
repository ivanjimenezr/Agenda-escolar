
import React, { useState } from 'react';
import type { StudentProfile, Subject, Exam, MenuItem, SchoolEvent, ActiveModules, DinnerItem, ModuleKey, Center, Contact, View } from '../types';
import { BookOpenIcon, CakeIcon, AcademicCapIcon, FlagIcon, MoonIcon, SparklesIcon, ChevronDownIcon, ChevronUpIcon, TrashIcon, PencilIcon, UserIcon, PlusIcon, PencilIcon as EditIcon, ChevronLeftIcon, ChevronRightIcon } from '../components/icons';
import { generateDinners } from '../services/dinnerService';
import { deleteEvent as deleteEventService, updateEvent } from '../services/eventService';
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
  const [dayOffset, setDayOffset] = useState(0);
  const [expandedExamId, setExpandedExamId] = useState<string | null>(null);
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

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
        // Call backend to generate dinner suggestion using AI
        const generatedDinners = await generateDinners(profile.id, {
          type: 'today',
          target_date: todayISO
        });

        if (generatedDinners && generatedDinners.length > 0) {
            // Transform backend format to frontend format
            const transformedDinners = generatedDinners.map(d => ({
                id: d.id,
                studentId: d.student_id,
                date: d.date,
                meal: d.meal,
                ingredients: d.ingredients
            }));

            // Update dinners state
            setDinners((prev: DinnerItem[]) => {
                const filtered = prev.filter(d => d.date !== todayISO);
                return [...filtered, ...transformedDinners];
            });
        }
    } catch (e: any) {
        console.error('Error generating dinner:', e);
        alert(e.message || 'Error al generar la cena. Por favor, intenta de nuevo.');
    } finally {
        setGenerating(false);
    }
  };

  const todaysMenu = menu.find(m => m.date === todayISO);
  const todaysDinner = dinners.find(d => d.date === todayISO);
  const upcomingExams = exams.filter(e => new Date(e.date) >= new Date(today.setHours(0,0,0,0))).sort((a,b) => a.date.localeCompare(b.date)).slice(0, 2);
  const upcomingEvents = events.filter(e => new Date(e.date) >= new Date(new Date().setHours(0,0,0,0))).sort((a,b) => a.date.localeCompare(b.date));

  // Check if subject time has passed
  const isSubjectPassed = (time: string): boolean => {
    if (dayOffset > 0) return false;
    const now = new Date();
    const [hours, minutes] = time.split(':').map(Number);
    const subjectTime = new Date();
    subjectTime.setHours(hours, minutes, 0, 0);
    return now > subjectTime;
  };

  const handleDeleteEvent = async (id: string) => {
    if (!confirm('¿Eliminar este evento?')) return;

    try {
      // Delete from backend first
      await deleteEventService(id);
      // Then update local state
      setEvents(prev => prev.filter(e => e.id !== id));
    } catch (error) {
      console.error('Error deleting event:', error);
      alert('Error al eliminar el evento. Por favor, intenta de nuevo.');
    }
  };

  const handleSaveEvent = async (data: any) => {
    if (!editingEvent) return;

    try {
      // Normalize event type to ensure correct capitalization
      const normalizeEventType = (type: string): 'Festivo' | 'Lectivo' | 'Vacaciones' => {
        const normalized = type.toLowerCase();
        if (normalized === 'festivo') return 'Festivo';
        if (normalized === 'lectivo') return 'Lectivo';
        if (normalized === 'vacaciones') return 'Vacaciones';
        return 'Lectivo';
      };

      const payload = {
        date: data.date,
        time: data.time || undefined,
        name: data.name,
        type: normalizeEventType(data.type),
        description: data.description || undefined
      };

      // Update in backend first
      const updatedEvent = await updateEvent(editingEvent.id, payload);

      // Then update local state
      setEvents(prev => prev.map(e => e.id === editingEvent.id ? {
        ...e,
        date: updatedEvent.date,
        time: updatedEvent.time,
        name: updatedEvent.name,
        type: normalizeEventType(updatedEvent.type),
        description: updatedEvent.description
      } : e));

      setEditingEvent(null);
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Error al actualizar el evento. Por favor, intenta de nuevo.');
    }
  };

  const renderModule = (key: ModuleKey, index: number) => {
      if (!activeModules[key]) return null;
      switch(key) {
          case 'subjects':
              const targetDate = new Date(today);
              targetDate.setDate(today.getDate() + dayOffset);
              const targetDayOfWeek = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'][targetDate.getDay()];
              const subjectsForDay = subjects
                .filter(s => s.days.includes(targetDayOfWeek as any))
                .sort((a, b) => a.time.localeCompare(b.time));

              const dateLabel = new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long' }).format(targetDate);

              return (
                <InfoCard 
                    key={key} 
                    icon={<BookOpenIcon />} 
                    title={dayOffset === 0 ? 'Clases de Hoy' : dateLabel}
                    index={index} 
                    isEditMode={isEditMode} 
                    onMoveUp={() => moveCard(index, 'up')} 
                    onMoveDown={() => moveCard(index, 'down')}
                >
                    <div className="flex items-center justify-between mb-3 px-1">
                        <button 
                            onClick={() => setDayOffset(d => Math.max(d - 1, 0))} 
                            disabled={dayOffset === 0}
                            className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-500 disabled:opacity-30"
                        >
                            <ChevronLeftIcon className="w-4 h-4" />
                        </button>
                        <span className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase">
                            {dayOffset === 0 ? 'Hoy' : targetDayOfWeek}
                        </span>
                        <button 
                            onClick={() => setDayOffset(d => Math.min(d + 1, 4))} 
                            disabled={dayOffset === 4}
                            className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-500 disabled:opacity-30"
                        >
                            <ChevronRightIcon className="w-4 h-4" />
                        </button>
                    </div>

                    {subjectsForDay.length > 0 ? subjectsForDay.map(s => {
                        const isPassed = isSubjectPassed(s.time);
                        return (
                        <div key={s.id} className={`flex items-center p-3 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm transition-all ${isPassed ? 'opacity-50' : ''}`}>
                            <div className="w-1.5 h-10 rounded-full mr-3" style={{ backgroundColor: isPassed ? '#9ca3af' : (s.color || (s.type === 'extraescolar' ? '#a855f7' : '#3b82f6')) }}></div>
                            <div className="flex-grow">
                                <div className="flex justify-between items-start">
                                    <p className={`font-bold text-sm ${isPassed ? 'text-gray-400 dark:text-gray-500 line-through' : 'text-gray-900 dark:text-gray-100'}`}>{s.name}</p>
                                    <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded-full border ${isPassed ? 'border-gray-300 text-gray-400 bg-gray-100 dark:bg-gray-800 dark:text-gray-500 dark:border-gray-700' : s.type === 'extraescolar' ? 'border-purple-200 text-purple-600 bg-purple-50 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800' : 'border-blue-200 text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800'}`}>
                                        {s.type === 'extraescolar' ? 'Extra' : 'Cole'}
                                    </span>
                                </div>
                                <p className={`text-xs font-medium ${isPassed ? 'text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-400'}`}>{s.time} • {s.teacher}</p>
                            </div>
                        </div>
                        );
                    }) : <p className="text-center py-3 text-gray-400 dark:text-gray-500 text-sm font-medium italic">No hay clases este día</p>}
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
                    {upcomingExams.length > 0 ? upcomingExams.map(e => {
                        const isExpanded = expandedExamId === e.id;
                        return (
                            <div key={e.id} className="rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 shadow-sm overflow-hidden">
                                <div
                                    className="p-3 flex justify-between items-center cursor-pointer hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                                    onClick={() => setExpandedExamId(isExpanded ? null : e.id)}
                                >
                                    <div className="flex-1 mr-2">
                                        <p className="font-bold text-red-950 dark:text-red-100 text-sm">{e.subject}</p>
                                        <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide">{e.topic}</p>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="text-right flex-shrink-0">
                                            <p className="text-base font-bold leading-none text-red-900 dark:text-red-200">{new Date(e.date).getDate()}</p>
                                            <p className="text-[9px] text-red-500/70 dark:text-red-400/70 font-bold uppercase">{new Date(e.date).toLocaleDateString('es-ES', { month: 'short' })}</p>
                                        </div>
                                        {isExpanded ? (
                                            <ChevronUpIcon className="w-4 h-4 text-red-600 dark:text-red-400" />
                                        ) : (
                                            <ChevronDownIcon className="w-4 h-4 text-red-600 dark:text-red-400" />
                                        )}
                                    </div>
                                </div>
                                {isExpanded && (
                                    <div className="px-3 pb-3 pt-2 border-t border-red-200 dark:border-red-900/50 bg-red-100/50 dark:bg-red-900/20">
                                        <div className="space-y-2">
                                            <div>
                                                <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide mb-1">Asignatura</p>
                                                <p className="text-sm text-red-950 dark:text-red-100 font-semibold">{e.subject}</p>
                                            </div>
                                            <div>
                                                <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide mb-1">Tema</p>
                                                <p className="text-sm text-red-950 dark:text-red-100">{e.topic}</p>
                                            </div>
                                            <div>
                                                <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide mb-1">Fecha</p>
                                                <p className="text-sm text-red-950 dark:text-red-100">
                                                    {new Date(e.date).toLocaleDateString('es-ES', {
                                                        weekday: 'long',
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric'
                                                    })}
                                                </p>
                                            </div>
                                            {e.notes && (
                                                <div>
                                                    <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide mb-1">Notas</p>
                                                    <p className="text-sm text-red-950 dark:text-red-100 whitespace-pre-wrap">{e.notes}</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    }) : <p className="text-center py-3 text-green-600 dark:text-green-400 text-sm font-bold">¡Sin exámenes pronto! 🎉</p>}
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
                      {upcomingEvents.map(ev => {
                          const isExpanded = expandedEventId === ev.id;
                          return (
                              <div key={ev.id} className="rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 shadow-sm overflow-hidden">
                                  <div
                                      className="p-3 flex justify-between items-center cursor-pointer hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors"
                                      onClick={() => setExpandedEventId(isExpanded ? null : ev.id)}
                                  >
                                      <div className="flex-1 mr-2">
                                          <p className="font-bold text-amber-950 dark:text-amber-100 text-sm">{ev.name}</p>
                                          <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide">{ev.type}</p>
                                      </div>
                                      <div className="flex items-center space-x-2">
                                          <div className="text-right flex-shrink-0">
                                              <p className="text-base font-bold leading-none text-amber-900 dark:text-amber-200">{new Date(ev.date).getDate()}</p>
                                              <p className="text-[9px] text-amber-500/70 dark:text-amber-400/70 font-bold uppercase">{new Date(ev.date).toLocaleDateString('es-ES', { month: 'short' })}</p>
                                          </div>
                                          {isExpanded ? (
                                              <ChevronUpIcon className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                                          ) : (
                                              <ChevronDownIcon className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                                          )}
                                      </div>
                                  </div>
                                  {isExpanded && (
                                      <div className="px-3 pb-3 pt-2 border-t border-amber-200 dark:border-amber-900/50 bg-amber-100/50 dark:bg-amber-900/20">
                                          <div className="space-y-2">
                                              <div>
                                                  <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide mb-1">Nombre</p>
                                                  <p className="text-sm text-amber-950 dark:text-amber-100 font-semibold">{ev.name}</p>
                                              </div>
                                              <div>
                                                  <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide mb-1">Tipo</p>
                                                  <p className="text-sm text-amber-950 dark:text-amber-100">{ev.type}</p>
                                              </div>
                                              <div>
                                                  <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide mb-1">Fecha</p>
                                                  <p className="text-sm text-amber-950 dark:text-amber-100">
                                                      {new Date(ev.date).toLocaleDateString('es-ES', {
                                                          weekday: 'long',
                                                          year: 'numeric',
                                                          month: 'long',
                                                          day: 'numeric'
                                                      })}
                                                  </p>
                                              </div>
                                              {ev.time && (
                                                  <div>
                                                      <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide mb-1">Hora</p>
                                                      <p className="text-sm text-amber-950 dark:text-amber-100">{ev.time}</p>
                                                  </div>
                                              )}
                                              {ev.description && (
                                                  <div>
                                                      <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wide mb-1">Descripción</p>
                                                      <p className="text-sm text-amber-950 dark:text-amber-100 whitespace-pre-wrap">{ev.description}</p>
                                                  </div>
                                              )}
                                              <div className="flex space-x-2 pt-2 border-t border-amber-200 dark:border-amber-900/50">
                                                  <button
                                                      onClick={(e) => { e.stopPropagation(); setEditingEvent(ev); }}
                                                      className="flex-1 p-2 text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                                                  >
                                                      Editar
                                                  </button>
                                                  <button
                                                      onClick={(e) => { e.stopPropagation(); handleDeleteEvent(ev.id); }}
                                                      className="flex-1 p-2 text-xs font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                                                  >
                                                      Eliminar
                                                  </button>
                                              </div>
                                          </div>
                                      </div>
                                  )}
                              </div>
                          );
                      })}
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

      {editingEvent && <ItemFormModal item={editingEvent} type="events" title="Evento" studentId={activeProfileId} onClose={() => setEditingEvent(null)} onSave={handleSaveEvent} />}
    </div>
  );
};
export default HomePage;
