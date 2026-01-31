
import React, { useState } from 'react';
import type { Subject, Exam, MenuItem, SchoolEvent, DinnerItem, ModuleKey, Center, Contact, StudentProfile } from '../types';

type Manageable = ModuleKey | 'centers' | 'profiles';
type Item = Subject | Exam | MenuItem | SchoolEvent | DinnerItem | Center | Contact | StudentProfile;

interface ItemFormModalProps {
    item: Item | null;
    type: Manageable;
    onClose: () => void;
    onSave: (data: any) => void;
    title: string;
    centers?: Center[];
}

const DAYS_OF_WEEK = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] as const;

const ItemFormModal: React.FC<ItemFormModalProps> = ({ item, type, onClose, onSave, title, centers }) => {
    const [formData, setFormData] = useState<any>(() => {
        if (item) return item;
        switch(type) {
            case 'subjects': return { name: '', days: ['Lunes'], time: '09:00', teacher: '', color: '#3b82f6', type: 'colegio' };
            case 'exams': return { subject: '', date: new Date().toISOString().split('T')[0], topic: '', notes: '' };
            case 'menu': return { date: new Date().toISOString().split('T')[0], mainCourse: '', sideDish: '', dessert: '' };
            case 'events': return { date: new Date().toISOString().split('T')[0], name: '', type: 'Lectivo' };
            case 'dinner': return { date: new Date().toISOString().split('T')[0], meal: '', ingredients: [] };
            case 'centers': return { name: '' };
            case 'contacts': return { centerId: centers?.[0]?.id || '', name: '', phone: '', role: '' };
            case 'profiles': return { name: '', school: '', grade: '', avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${Date.now()}`, allergies: [], excludedFoods: [] };
            default: return {};
        }
    });

    const toggleDay = (day: string) => {
        const currentDays = formData.days || [];
        if (currentDays.includes(day)) {
            if (currentDays.length > 1) {
                setFormData({ ...formData, days: currentDays.filter((d: string) => d !== day) });
            }
        } else {
            setFormData({ ...formData, days: [...currentDays, day] });
        }
    };

    // Estilos optimizados: Borde gris 200 para mejor definición, texto explícito por tema.
    const inputClass = "w-full p-4 bg-white dark:bg-gray-950 rounded-2xl font-semibold border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-gray-100 outline-none transition-all focus:ring-2 focus:ring-blue-500 shadow-sm";
    const labelClass = "block text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1.5 ml-1";

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex justify-center items-end p-4 z-[100]">
            <div className="bg-gray-50 dark:bg-gray-900 rounded-[2.5rem] w-full max-w-md p-7 shadow-2xl animate-in slide-in-from-bottom duration-300 max-h-[90vh] overflow-y-auto scrollbar-hide">
                <header className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-black text-gray-900 dark:text-white leading-none">{item ? 'Editar' : 'Añadir'} {title}</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 w-10 h-10 flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-full font-bold">✕</button>
                </header>
                
                <div className="space-y-5">
                    {/* Perfiles */}
                    {type === 'profiles' && (
                        <>
                            <div>
                                <label className={labelClass}>Nombre del Estudiante</label>
                                <input className={inputClass} placeholder="Ej: Alex García" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Colegio</label>
                                <input className={inputClass} placeholder="Ej: Colegio Cervantes" value={formData.school} onChange={e => setFormData({...formData, school: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Curso</label>
                                <input className={inputClass} placeholder="Ej: 5º Primaria" value={formData.grade} onChange={e => setFormData({...formData, grade: e.target.value})} />
                            </div>
                        </>
                    )}

                    {/* Sujetos / Clases */}
                    {type === 'subjects' && (
                        <>
                            <div>
                                <label className={labelClass}>Asignatura / Actividad</label>
                                <input className={inputClass} placeholder="Ej: Matemáticas" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Tipo de Clase</label>
                                <div className="grid grid-cols-2 gap-3">
                                    <button 
                                        type="button"
                                        onClick={() => setFormData({...formData, type: 'colegio', color: '#3b82f6'})}
                                        className={`p-4 rounded-2xl border-2 text-xs font-black transition-all ${formData.type === 'colegio' ? 'bg-blue-50 border-blue-500 text-blue-600 dark:bg-blue-900/30 dark:border-blue-400 dark:text-blue-200' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-400'}`}
                                    >COLEGIO</button>
                                    <button 
                                        type="button"
                                        onClick={() => setFormData({...formData, type: 'extraescolar', color: '#a855f7'})}
                                        className={`p-4 rounded-2xl border-2 text-xs font-black transition-all ${formData.type === 'extraescolar' ? 'bg-purple-50 border-purple-500 text-purple-600 dark:bg-purple-900/30 dark:border-purple-400 dark:text-purple-200' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-400'}`}
                                    >EXTRAESCOLAR</button>
                                </div>
                            </div>
                            <div>
                                <label className={labelClass}>Días de la semana</label>
                                <div className="flex flex-wrap gap-2">
                                    {DAYS_OF_WEEK.map(day => {
                                        const isSelected = (formData.days || []).includes(day);
                                        return (
                                            <button
                                                key={day}
                                                type="button"
                                                onClick={() => toggleDay(day)}
                                                className={`px-3 py-3 rounded-xl text-[10px] font-black border-2 transition-all ${
                                                    isSelected 
                                                    ? 'bg-blue-600 border-blue-600 text-white shadow-md scale-105' 
                                                    : 'bg-white border-gray-200 text-gray-400 dark:bg-gray-800 dark:border-gray-700'
                                                }`}
                                            >
                                                {day.substring(0, 3).toUpperCase()}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className={labelClass}>Hora</label>
                                    <input className={inputClass} type="time" value={formData.time} onChange={e => setFormData({...formData, time: e.target.value})} />
                                </div>
                                <div>
                                    <label className={labelClass}>Color</label>
                                    <input className={`${inputClass} h-[54px] p-1`} type="color" value={formData.color} onChange={e => setFormData({...formData, color: e.target.value})} />
                                </div>
                            </div>
                            <div>
                                <label className={labelClass}>Profesor / Instructor</label>
                                <input className={inputClass} placeholder="Nombre" value={formData.teacher} onChange={e => setFormData({...formData, teacher: e.target.value})} />
                            </div>
                        </>
                    )}

                    {/* Centros y Contactos */}
                    {type === 'centers' && (
                        <div>
                            <label className={labelClass}>Nombre del Centro</label>
                            <input className={inputClass} placeholder="Ej: Colegio o Academia" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                        </div>
                    )}

                    {type === 'contacts' && (
                        <>
                            <div>
                                <label className={labelClass}>Centro Asociado</label>
                                <select className={inputClass} value={formData.centerId} onChange={e => setFormData({...formData, centerId: e.target.value})}>
                                    {centers?.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className={labelClass}>Nombre</label>
                                <input className={inputClass} placeholder="Nombre del contacto" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Teléfono</label>
                                <input className={inputClass} placeholder="600 000 000" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
                            </div>
                        </>
                    )}

                    {/* Exámenes y Menú */}
                    {(type === 'exams' || type === 'menu' || type === 'events' || type === 'dinner') && (
                        <div>
                            <label className={labelClass}>Fecha</label>
                            <input className={inputClass} type="date" value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} />
                        </div>
                    )}
                    {type === 'exams' && (
                        <>
                            <div>
                                <label className={labelClass}>Asignatura</label>
                                <input className={inputClass} placeholder="Ej: Lengua" value={formData.subject} onChange={e => setFormData({...formData, subject: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Tema</label>
                                <input className={inputClass} placeholder="Contenido del examen" value={formData.topic} onChange={e => setFormData({...formData, topic: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Notas</label>
                                <textarea className={`${inputClass} min-h-[100px]`} placeholder="Detalles adicionales..." value={formData.notes || ''} onChange={e => setFormData({...formData, notes: e.target.value})} />
                            </div>
                        </>
                    )}
                    {type === 'menu' && (
                        <div className="space-y-4">
                            <div>
                                <label className={labelClass}>Primer Plato</label>
                                <input className={inputClass} placeholder="Principal" value={formData.mainCourse} onChange={e => setFormData({...formData, mainCourse: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Segundo / Guarnición</label>
                                <input className={inputClass} placeholder="Secundario" value={formData.sideDish} onChange={e => setFormData({...formData, sideDish: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Postre</label>
                                <input className={inputClass} placeholder="Postre" value={formData.dessert} onChange={e => setFormData({...formData, dessert: e.target.value})} />
                            </div>
                        </div>
                    )}
                </div>

                <div className="flex space-x-3 mt-10">
                    <button onClick={onClose} className="flex-1 p-4 bg-white dark:bg-gray-800 rounded-[1.25rem] font-black text-xs uppercase tracking-widest text-gray-500 border border-gray-200 dark:border-gray-700 active:scale-95 transition-all">Cancelar</button>
                    <button onClick={() => {
                        // Normalize form values: trim strings and avoid sending empty strings
                        const normalized: any = { ...formData };
                        if (typeof normalized.mainCourse === 'string') normalized.mainCourse = normalized.mainCourse.trim();
                        if (typeof normalized.sideDish === 'string') normalized.sideDish = normalized.sideDish.trim();
                        if (typeof normalized.dessert === 'string') normalized.dessert = normalized.dessert.trim();

                        if (normalized.mainCourse === '') delete normalized.mainCourse;
                        if (normalized.sideDish === '') delete normalized.sideDish;
                        if (normalized.dessert === '') delete normalized.dessert;

                        // Debug: log normalized form data before sending
                        console.debug('[ItemFormModal] normalized formData:', normalized);

                        onSave(normalized);
                    }} className="flex-1 p-4 bg-blue-600 text-white rounded-[1.25rem] font-black text-xs uppercase tracking-widest shadow-xl active:scale-95 transition-all">Guardar</button>
                </div>
            </div>
        </div>
    );
};

export default ItemFormModal;
