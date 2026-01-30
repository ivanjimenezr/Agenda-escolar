
import React, { useState, useEffect, useRef } from 'react';
import type { StudentProfile, ActiveModules, ModuleKey } from '../types';
import { PlusIcon, TrashIcon, UserIcon, PencilIcon, MoonIcon, SunIcon } from '../components/icons';
import ItemFormModal from '../components/ItemFormModal';

interface ProfilePageProps {
  profile: StudentProfile;
  profiles: StudentProfile[];
  setProfiles: React.Dispatch<React.SetStateAction<StudentProfile[]>>;
  setProfile: (updated: StudentProfile | ((prev: StudentProfile) => StudentProfile)) => void;
  activeProfileId: string;
  setActiveProfileId: (id: string) => void;
  activeModules: ActiveModules;
  setActiveModules: (val: ActiveModules | ((prev: ActiveModules) => ActiveModules)) => void;
  theme: 'light' | 'dark';
  setTheme: (t: 'light' | 'dark') => void;
  onLogout: () => void;
}

const moduleLabels: Record<ModuleKey, string> = {
    subjects: 'Horario de Clases',
    exams: 'Exámenes',
    menu: 'Menú del Comedor',
    events: 'Calendario Escolar',
    dinner: 'Módulo de Cenas',
    contacts: 'Directorio'
};

const APP_AVATARS = ['Alex', 'Jordan', 'Taylor', 'Charlie', 'Casey', 'Robin', 'Sam', 'Mika'].map(seed => `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}`);

const ProfilePage: React.FC<ProfilePageProps> = ({ profile, profiles, setProfiles, setProfile, activeProfileId, setActiveProfileId, activeModules, setActiveModules, theme, setTheme, onLogout }) => {
  const [formData, setFormData] = useState(profile);
  const [isEditing, setIsEditing] = useState(false);
  const [newExcluded, setNewExcluded] = useState('');
  const [isChildModalOpen, setIsChildModalOpen] = useState(false);
  const [isAvatarPickerOpen, setIsAvatarPickerOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { setFormData(profile); }, [profile]);

  const handleSaveMainInfo = () => { setProfile(formData); setIsEditing(false); };
  const handleAllergyToggle = (allergy: string) => {
      const current = profile.allergies || [];
      const updated = current.includes(allergy) ? current.filter(a => a !== allergy) : [...current, allergy];
      setProfile({ ...profile, allergies: updated });
  };
  const addExcluded = () => {
      if (!newExcluded.trim()) return;
      const current = profile.excludedFoods || [];
      if (!current.includes(newExcluded.trim())) setProfile({ ...profile, excludedFoods: [...current, newExcluded.trim()] });
      setNewExcluded('');
  };
  const removeExcluded = (food: string) => setProfile({ ...profile, excludedFoods: (profile.excludedFoods || []).filter(f => f !== food) });
  const handleModuleToggle = (key: ModuleKey) => setActiveModules(prev => ({ ...prev, [key]: !prev[key] }));
  const deleteChild = (id: string) => { if (profiles.length > 1 && confirm('¿Borrar perfil?')) { const updated = profiles.filter(p => p.id !== id); setProfiles(updated); setActiveProfileId(updated[0].id); } };
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
          const reader = new FileReader();
          reader.onloadend = () => { setProfile({ ...profile, avatarUrl: reader.result as string }); setIsAvatarPickerOpen(false); };
          reader.readAsDataURL(file);
      }
  };

  const inputClass = "w-full p-3 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-xl border border-gray-200 dark:border-gray-700 text-sm font-medium shadow-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all";

  return (
    <div className="p-5 pb-24 animate-in fade-in duration-500 bg-gray-50 dark:bg-gray-950 min-h-full transition-colors">
      <div className="max-w-md mx-auto space-y-6">
        
        {/* Gestión de Hijos */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex justify-between items-center">
                <span>Gestionar Hijos</span>
                <button onClick={() => setIsChildModalOpen(true)} className="p-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg"><PlusIcon className="w-4 h-4" /></button>
            </h2>
            <div className="space-y-2">
                {profiles.map(p => (
                    <div key={p.id} className={`flex items-center justify-between p-3 rounded-xl border transition-colors ${activeProfileId === p.id ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800' : 'bg-gray-50 border-gray-100 dark:bg-gray-900 dark:border-gray-800'}`}>
                        <div className="flex items-center flex-1 cursor-pointer" onClick={() => setActiveProfileId(p.id)}>
                            <img src={p.avatarUrl} className="w-10 h-10 rounded-full mr-3 border border-white dark:border-gray-700 shadow-sm" alt={p.name} />
                            <div><p className="text-sm font-bold dark:text-gray-200">{p.name}</p><p className="text-[10px] text-gray-500">{p.grade}</p></div>
                        </div>
                        <button onClick={() => deleteChild(p.id)} className="p-2 text-red-400 hover:text-red-600 transition-colors"><TrashIcon className="w-4 h-4" /></button>
                    </div>
                ))}
            </div>
        </div>

        {/* Perfil Seleccionado */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 flex flex-col items-center border border-gray-200 dark:border-gray-700">
            <div className="relative cursor-pointer group" onClick={() => setIsAvatarPickerOpen(true)}>
                <img src={profile.avatarUrl} className="w-24 h-24 rounded-2xl object-cover mb-4 shadow-md border-4 border-white dark:border-gray-700 group-hover:opacity-90 transition-all" alt="Avatar" />
                <div className="absolute -bottom-1 -right-1 bg-blue-600 text-white p-1.5 rounded-lg border-2 border-white dark:border-gray-800 shadow-sm"><PlusIcon className="w-3 h-3" /></div>
            </div>
            {!isEditing ? (
                 <div className="text-center">
                    <h1 className="text-xl font-bold dark:text-white">{formData.name}</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{formData.school} • {formData.grade}</p>
                    <button onClick={() => setIsEditing(true)} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-xl font-bold text-xs uppercase tracking-wider active:scale-95 transition-all shadow-sm">Editar Datos</button>
                 </div>
            ) : (
                <div className="w-full space-y-4 animate-in slide-in-from-top duration-200">
                    <div>
                      <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 ml-1 block">Nombre</label>
                      <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className={inputClass} />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 ml-1 block">Colegio</label>
                      <input type="text" value={formData.school} onChange={e => setFormData({...formData, school: e.target.value})} className={inputClass} />
                    </div>
                    <div className="flex space-x-2 pt-2">
                      <button onClick={() => setIsEditing(false)} className="flex-1 py-3 bg-gray-100 dark:bg-gray-700 dark:text-gray-300 rounded-xl text-xs font-bold uppercase border border-gray-200 dark:border-gray-600">Cancelar</button>
                      <button onClick={handleSaveMainInfo} className="flex-1 py-3 bg-blue-600 text-white rounded-xl text-xs font-bold uppercase shadow-lg">Guardar</button>
                    </div>
                </div>
            )}
        </div>

        {/* Configuración de la Aplicación (Tema) */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-base font-bold text-gray-900 dark:text-white mb-4">Configuración de la App</h2>
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        {theme === 'light' ? <SunIcon className="w-5 h-5 mr-3 text-amber-500" /> : <MoonIcon className="w-5 h-5 mr-3 text-indigo-400" />}
                        <span className="text-sm font-medium dark:text-gray-300">Modo {theme === 'light' ? 'Claro' : 'Oscuro'}</span>
                    </div>
                    <button 
                      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                      className={`w-14 h-8 rounded-full p-1 transition-colors duration-300 flex items-center ${theme === 'dark' ? 'bg-indigo-600' : 'bg-gray-200 shadow-inner'}`}
                    >
                        <div className={`w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-300 flex items-center justify-center ${theme === 'dark' ? 'translate-x-6' : 'translate-x-0'}`}>
                            {theme === 'dark' ? <MoonIcon className="w-3.5 h-3.5 text-indigo-600" /> : <SunIcon className="w-3.5 h-3.5 text-amber-500" />}
                        </div>
                    </button>
                </div>
                <button 
                    onClick={onLogout}
                    className="w-full py-3 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 rounded-xl text-xs font-black uppercase tracking-widest border border-red-100 dark:border-red-900/20 active:scale-95 transition-all"
                >
                    Cerrar Sesión
                </button>
            </div>
        </div>

        {/* Configuración Dietética */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-base font-bold dark:text-white mb-4">Configuración Dietética</h2>
            <div className="space-y-6">
                <div>
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Alergias</p>
                    <div className="grid grid-cols-2 gap-3">
                        {['Sin Gluten', 'Sin Lactosa'].map((label, idx) => {
                            const key = idx === 0 ? 'gluten' : 'lactose';
                            const active = (profile.allergies || []).includes(key);
                            return <button key={key} onClick={() => handleAllergyToggle(key)} className={`p-3 rounded-xl border-2 font-bold text-xs transition-all ${active ? 'bg-red-50 border-red-200 text-red-600 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400 shadow-sm' : 'bg-white border-gray-100 text-gray-400 dark:bg-gray-900 dark:border-gray-700'}`}>{label.toUpperCase()}</button>;
                        })}
                    </div>
                </div>
                <div>
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Excluidos</p>
                    <div className="flex space-x-2 mb-3">
                      <input type="text" value={newExcluded} onChange={e => setNewExcluded(e.target.value)} onKeyDown={e => e.key === 'Enter' && addExcluded()} placeholder="Añadir..." className={inputClass} />
                      <button onClick={addExcluded} className="p-3 bg-blue-600 text-white rounded-xl shadow-md active:scale-95 transition-all"><PlusIcon className="w-5 h-5" /></button>
                    </div>
                    <div className="flex flex-wrap gap-2">{(profile.excludedFoods || []).map(food => <span key={food} className="inline-flex items-center px-3 py-1 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full text-xs font-bold border border-gray-200 dark:border-gray-600 shadow-sm">{food}<button onClick={() => removeExcluded(food)} className="ml-2 text-red-400 font-bold p-1">✕</button></span>)}</div>
                </div>
            </div>
        </div>

        {/* Visibilidad de Módulos */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-base font-bold dark:text-white mb-4">Módulos Activos</h2>
            <div className="space-y-4">
                {(Object.keys(moduleLabels) as ModuleKey[]).map(key => (
                    <div key={key} className="flex items-center justify-between py-1">
                        <span className="text-sm font-medium dark:text-gray-300">{moduleLabels[key]}</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" checked={activeModules[key] || false} onChange={() => handleModuleToggle(key)} className="sr-only peer" />
                            <div className="w-10 h-5 bg-gray-200 dark:bg-gray-700 rounded-full peer peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-5 shadow-inner"></div>
                        </label>
                    </div>
                ))}
            </div>
        </div>
      </div>

      {/* Selector de Avatar Modal (Bottom Sheet Style) */}
      {isAvatarPickerOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] flex items-end justify-center p-4 animate-in fade-in duration-300" onClick={() => setIsAvatarPickerOpen(false)}>
              <div className="bg-white dark:bg-gray-900 w-full max-w-md rounded-t-3xl p-6 shadow-2xl animate-in slide-in-from-bottom duration-300" onClick={e => e.stopPropagation()}>
                  <div className="w-12 h-1 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-6"></div>
                  <h3 className="text-lg font-bold dark:text-white mb-6">Cambiar Foto de Perfil</h3>
                  <div className="space-y-6">
                      <button onClick={() => fileInputRef.current?.click()} className="w-full p-4 bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-200 dark:border-blue-800 rounded-2xl text-blue-600 dark:text-blue-400 font-bold active:scale-[0.98] transition-all shadow-sm">Subir foto del dispositivo</button>
                      <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="image/*" className="hidden" />
                      <div>
                          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4">Avatares Predefinidos</p>
                          <div className="grid grid-cols-4 gap-3 max-h-[30vh] overflow-y-auto pr-2 scrollbar-hide">
                              {APP_AVATARS.map((url, i) => <button key={i} onClick={() => { setProfile({ ...profile, avatarUrl: url }); setIsAvatarPickerOpen(false); }} className={`rounded-xl overflow-hidden border-2 transition-all active:scale-95 ${profile.avatarUrl === url ? 'border-blue-500 scale-105 shadow-md' : 'border-gray-200 dark:border-gray-800'}`}><img src={url} className="w-full h-full object-cover" /></button>)}
                          </div>
                      </div>
                      <button onClick={() => setIsAvatarPickerOpen(false)} className="w-full py-4 bg-gray-100 dark:bg-gray-800 rounded-2xl font-bold text-gray-500 dark:text-gray-400 uppercase text-xs active:scale-95 transition-all">Cerrar</button>
                  </div>
              </div>
          </div>
      )}

      {isChildModalOpen && <ItemFormModal item={null} type="profiles" title="Nuevo Hijo/a" onClose={() => setIsChildModalOpen(false)} onSave={(data) => { const newId = `child-${Date.now()}`; setProfiles(prev => [...prev, { ...data, id: newId, activeModules: { subjects: true, exams: true, menu: true, events: true, dinner: true, contacts: true } }]); setActiveProfileId(newId); setIsChildModalOpen(false); }} />}
    </div>
  );
};
export default ProfilePage;
