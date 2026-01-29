
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
    centers?: Center[]; // Necesario para asociar contactos a centros
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

    // Estilos mejorados para inputs: fondo blanco en light, gris oscuro en dark, texto contrastado siempre.
    const inputClass = "w-full p-3 bg-white dark:bg-gray-950 rounded-xl font-medium border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-gray-100 outline-none transition-all focus:ring-2 focus:ring-blue-500 shadow-sm";
    const labelClass = "block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1 ml-1";

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-end p-4 z-[100]">
            <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl w-full max-w-md p-6 shadow-2xl animate-in slide-in-from-bottom duration-300 max-h-[90vh] overflow-y-auto">
                <header className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">{item ? 'Editar' : 'Añadir'} {title}</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-2">✕</button>
                </header>
                
                <div className="space-y-4">
                    {/* Perfiles */}
                    {type === 'profiles' && (
                        <>
                            <div>
                                <label className={labelClass}>Nombre del Hijo/a</label>
                                <input className={inputClass} placeholder="Nombre" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
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
                                <input className={inputClass} placeholder="Ej: Matemáticas o Judo" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Tipo de Clase</label>
                                <div className="grid grid-cols-2 gap-2">
                                    <button 
                                        type="button"
                                        onClick={() => setFormData({...formData, type: 'colegio', color: '#3b82f6'})}
                                        className={`p-3 rounded-xl border-2 text-xs font-bold transition-all ${formData.type === 'colegio' ? 'bg-blue-50 border-blue-500 text-blue-600 dark:bg-blue-900/30 dark:border-blue-400 dark:text-blue-200' : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 text-gray-400'}`}
                                    >COLEGIO</button>
                                    <button 
                                        type="button"
                                        onClick={() => setFormData({...formData, type: 'extraescolar', color: '#a855f7'})}
                                        className={`p-3 rounded-xl border-2 text-xs font-bold transition-all ${formData.type === 'extraescolar' ? 'bg-purple-50 border-purple-500 text-purple-600 dark:bg-purple-900/30 dark:border-purple-400 dark:text-purple-200' : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 text-gray-400'}`}
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
                                                className={`px-3 py-2 rounded-lg text-[10px] font-bold border-2 transition-all ${
                                                    isSelected 
                                                    ? 'bg-blue-600 border-blue-600 text-white shadow-sm' 
                                                    : 'bg-white border-gray-100 text-gray-400 dark:bg-gray-800 dark:border-gray-700'
                                                }`}
                                            >
                                                {day.substring(0, 3).toUpperCase()}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                            <div>
                                <label className={labelClass}>Hora</label>
                                <input className={inputClass} type="time" value={formData.time} onChange={e => setFormData({...formData, time: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Profesor / Instructor</label>
                                <input className={inputClass} placeholder="Nombre del profesor" value={formData.teacher} onChange={e => setFormData({...formData, teacher: e.target.value})} />
                            </div>
                        </>
                    )}

                    {/* Centros */}
                    {type === 'centers' && (
                        <div>
                            <label className={labelClass}>Nombre del Centro</label>
                            <input className={inputClass} placeholder="Ej: Colegio Cervantes o Gimsanio" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                        </div>
                    )}

                    {/* Contactos */}
                    {type === 'contacts' && (
                        <>
                            <div>
                                <label className={labelClass}>Centro</label>
                                <select className={inputClass} value={formData.centerId} onChange={e => setFormData({...formData, centerId: e.target.value})}>
                                    {centers?.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className={labelClass}>Nombre del Contacto</label>
                                <input className={inputClass} placeholder="Ej: Tutor Juan" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Teléfono / Email</label>
                                <input className={inputClass} placeholder="600 000 000" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Cargo / Nota</label>
                                <input className={inputClass} placeholder="Ej: Profesor de Mates" value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})} />
                            </div>
                        </>
                    )}

                    {/* Otros (Exámenes, Menú, Eventos) */}
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
                                <input className={inputClass} placeholder="Ej: Historia" value={formData.subject} onChange={e => setFormData({...formData, subject: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Tema / Contenido</label>
                                <input className={inputClass} placeholder="Ej: Revolución Francesa" value={formData.topic} onChange={e => setFormData({...formData, topic: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Notas (Opcional)</label>
                                <textarea 
                                    className={`${inputClass} min-h-[80px]`} 
                                    placeholder="Detalles sobre el examen..." 
                                    value={formData.notes || ''} 
                                    onChange={e => setFormData({...formData, notes: e.target.value})} 
                                />
                            </div>
                        </>
                    )}
                    {type === 'menu' && (
                        <>
                            <div className="space-y-3 pt-2">
                                <div>
                                    <label className={labelClass}>Plato Principal</label>
                                    <input className={inputClass} placeholder="Ej: Lentejas con chorizo" value={formData.mainCourse} onChange={e => setFormData({...formData, mainCourse: e.target.value})} />
                                </div>
                                <div>
                                    <label className={labelClass}>Guarnición / Segundo</label>
                                    <input className={inputClass} placeholder="Ej: Filete de ternera" value={formData.sideDish} onChange={e => setFormData({...formData, sideDish: e.target.value})} />
                                </div>
                                <div>
                                    <label className={labelClass}>Postre</label>
                                    <input className={inputClass} placeholder="Ej: Fruta de temporada" value={formData.dessert} onChange={e => setFormData({...formData, dessert: e.target.value})} />
                                </div>
                            </div>
                        </>
                    )}
                    {type === 'events' && (
                        <>
                            <div>
                                <label className={labelClass}>Nombre del Evento</label>
                                <input className={inputClass} placeholder="Ej: Excursión al museo" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                            </div>
                            <div>
                                <label className={labelClass}>Tipo</label>
                                <select className={inputClass} value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})}>
                                    <option value="Lectivo">Lectivo</option>
                                    <option value="Festivo">Festivo</option>
                                    <option value="Vacaciones">Vacaciones</option>
                                </select>
                            </div>
                        </>
                    )}
                </div>

                <div className="flex space-x-2 mt-8">
                    <button onClick={onClose} className="flex-1 p-3 bg-white dark:bg-gray-800 rounded-xl font-bold text-xs uppercase tracking-wider text-gray-500 border border-gray-200 dark:border-gray-700">Cancelar</button>
                    <button onClick={() => onSave(formData)} className="flex-1 p-3 bg-blue-600 text-white rounded-xl font-bold text-xs uppercase tracking-wider shadow-lg active:scale-95">Guardar</button>
                </div>
            </div>
        </div>
    );
};

export default ItemFormModal;
