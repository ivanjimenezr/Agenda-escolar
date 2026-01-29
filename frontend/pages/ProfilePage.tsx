
import React, { useState, useEffect, useRef } from 'react';
import type { StudentProfile, ActiveModules, ModuleKey } from '../types';
import { PlusIcon, TrashIcon, UserIcon, PencilIcon } from '../components/icons';
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
}

const moduleLabels: Record<ModuleKey, string> = {
    subjects: 'Horario de Clases',
    exams: 'Exámenes',
    menu: 'Menú del Comedor',
    events: 'Calendario Escolar',
    dinner: 'Módulo de Cenas',
    contacts: 'Directorio'
};

// Avatares predefinidos de la app (DiceBear para ligereza)
const APP_AVATARS = [
    'Alex', 'Jordan', 'Taylor', 'Charlie', 'Casey', 'Robin', 'Sam', 'Mika', 
    'Kim', 'Jamie', 'Ariel', 'Ren', 'Sasha', 'Puck', 'Kore', 'Fenrir'
].map(seed => `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}`);

const ProfilePage: React.FC<ProfilePageProps> = ({ profile, profiles, setProfiles, setProfile, activeProfileId, setActiveProfileId, activeModules, setActiveModules }) => {
  const [formData, setFormData] = useState(profile);
  const [isEditing, setIsEditing] = useState(false);
  const [newExcluded, setNewExcluded] = useState('');
  const [isChildModalOpen, setIsChildModalOpen] = useState(false);
  const [isAvatarPickerOpen, setIsAvatarPickerOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
      setFormData(profile);
  }, [profile]);

  const handleSaveMainInfo = () => {
    setProfile(formData);
    setIsEditing(false);
  };

  const handleAllergyToggle = (allergy: string) => {
      const current = profile.allergies || [];
      const updated = current.includes(allergy) 
        ? current.filter(a => a !== allergy) 
        : [...current, allergy];
      setProfile({ ...profile, allergies: updated });
  };

  const addExcluded = () => {
      if (!newExcluded.trim()) return;
      const current = profile.excludedFoods || [];
      if (!current.includes(newExcluded.trim())) {
          const updated = [...current, newExcluded.trim()];
          setProfile({ ...profile, excludedFoods: updated });
      }
      setNewExcluded('');
  };

  const removeExcluded = (food: string) => {
      const current = profile.excludedFoods || [];
      const updated = current.filter(f => f !== food);
      setProfile({ ...profile, excludedFoods: updated });
  };

  const handleModuleToggle = (key: ModuleKey) => {
      setActiveModules(prev => ({
          ...prev,
          [key]: !prev[key]
      }));
  };

  const deleteChild = (id: string) => {
      if (profiles.length <= 1) {
          alert('Debes tener al menos un perfil.');
          return;
      }
      if (confirm('¿Seguro que quieres eliminar este perfil? Se perderán sus datos individuales.')) {
          const updated = profiles.filter(p => p.id !== id);
          setProfiles(updated);
          setActiveProfileId(updated[0].id);
      }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
          const reader = new FileReader();
          reader.onloadend = () => {
              const base64String = reader.result as string;
              setProfile({ ...profile, avatarUrl: base64String });
              setIsAvatarPickerOpen(false);
          };
          reader.readAsDataURL(file);
      }
  };

  const selectAppAvatar = (url: string) => {
      setProfile({ ...profile, avatarUrl: url });
      setIsAvatarPickerOpen(false);
  };

  return (
    <div className="p-5 pb-24 animate-in fade-in duration-500">
      <div className="max-w-md mx-auto space-y-6">
        
        {/* Gestión de Hijos */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex justify-between items-center">
                <span>Gestionar Hijos</span>
                <button onClick={() => setIsChildModalOpen(true)} className="p-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-lg active:scale-95">
                    <PlusIcon className="w-4 h-4" />
                </button>
            </h2>
            <div className="space-y-2">
                {profiles.map(p => (
                    <div key={p.id} className={`flex items-center justify-between p-3 rounded-xl border transition-all ${activeProfileId === p.id ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/10 dark:border-blue-800' : 'bg-gray-50 border-gray-100 dark:bg-gray-900 dark:border-gray-700'}`}>
                        <div className="flex items-center flex-1 cursor-pointer" onClick={() => setActiveProfileId(p.id)}>
                            <img src={p.avatarUrl} className="w-10 h-10 rounded-full mr-3 border border-white" alt={p.name} />
                            <div>
                                <p className={`text-sm font-bold ${activeProfileId === p.id ? 'text-blue-700 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'}`}>{p.name}</p>
                                <p className="text-[10px] text-gray-500">{p.grade}</p>
                            </div>
                        </div>
                        <button onClick={() => deleteChild(p.id)} className="p-2 text-red-400 hover:text-red-600">
                            <TrashIcon className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>
        </div>

        {/* Perfil Seleccionado con Selector de Avatar */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 flex flex-col items-center border border-gray-100 dark:border-gray-700">
            <div className="relative group cursor-pointer" onClick={() => setIsAvatarPickerOpen(true)}>
                <img src={profile.avatarUrl} className="w-24 h-24 rounded-2xl object-cover mb-4 shadow-md border-4 border-white dark:border-gray-700 group-hover:opacity-80 transition-opacity" alt="Avatar" />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="bg-black/40 rounded-2xl p-2 text-white">
                        <PencilIcon className="w-6 h-6" />
                    </div>
                </div>
                <div className="absolute -bottom-1 -right-1 bg-blue-600 text-white p-1.5 rounded-lg border-2 border-white dark:border-gray-800 shadow-sm">
                    <PlusIcon className="w-3 h-3" />
                </div>
            </div>

            {!isEditing ? (
                 <div className="text-center">
                    <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">{formData.name}</h1>
                    <p className="text-sm text-gray-500 font-medium">{formData.school} • {formData.grade}</p>
                    <button onClick={() => setIsEditing(true)} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-xl font-bold text-xs uppercase tracking-wider shadow-sm active:scale-95 transition-all">
                        Editar Datos de {formData.name.split(' ')[0]}
                    </button>
                 </div>
            ) : (
                <div className="w-full space-y-4">
                    <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700 text-sm font-medium" placeholder="Nombre" />
                    <input type="text" value={formData.school} onChange={e => setFormData({...formData, school: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700 text-sm font-medium" placeholder="Colegio" />
                    <input type="text" value={formData.grade} onChange={e => setFormData({...formData, grade: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700 text-sm font-medium" placeholder="Curso" />
                    <div className="flex space-x-2 pt-2">
                        <button onClick={() => setIsEditing(false)} className="flex-1 py-2 bg-gray-100 dark:bg-gray-700 rounded-xl text-xs font-bold uppercase">Cancelar</button>
                        <button onClick={handleSaveMainInfo} className="flex-1 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold uppercase">Guardar</button>
                    </div>
                </div>
            )}
        </div>

        {/* Configuración Dietética */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4">Configuración Dietética</h2>
            <div className="space-y-6">
                <div>
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Alergias / Intolerancias</p>
                    <div className="grid grid-cols-2 gap-3">
                        {['Sin Gluten', 'Sin Lactosa'].map((label, idx) => {
                            const key = idx === 0 ? 'gluten' : 'lactose';
                            const active = (profile.allergies || []).includes(key);
                            return (
                                <button 
                                    key={key}
                                    type="button"
                                    onClick={() => handleAllergyToggle(key)}
                                    className={`p-3 rounded-xl border-2 transition-all font-bold text-xs ${active ? 'bg-red-50 border-red-200 text-red-600' : 'bg-gray-50 border-gray-100 text-gray-400 dark:bg-gray-900 dark:border-gray-700'}`}
                                >
                                    {label.toUpperCase()}
                                </button>
                            );
                        })}
                    </div>
                </div>
                <div>
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Alimentos Excluidos</p>
                    <div className="flex space-x-2 mb-3">
                        <input 
                            type="text" 
                            value={newExcluded}
                            onChange={e => setNewExcluded(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && addExcluded()}
                            placeholder="Ej: Pescado, Frutos secos..." 
                            className="flex-grow p-3 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700 text-sm font-medium outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button onClick={addExcluded} className="p-3 bg-blue-600 text-white rounded-xl shadow-sm active:scale-95"><PlusIcon className="w-5 h-5" /></button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {(profile.excludedFoods || []).map(food => (
                            <span key={food} className="inline-flex items-center px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full text-xs font-bold border border-gray-200 dark:border-gray-600">
                                {food}
                                <button onClick={() => removeExcluded(food)} className="ml-2 text-red-400 hover:text-red-600 font-bold">✕</button>
                            </span>
                        ))}
                        {(!profile.excludedFoods || profile.excludedFoods.length === 0) && (
                            <p className="text-xs text-gray-400 italic">No hay alimentos excluidos para {profile.name.split(' ')[0]}.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* Visibilidad de Módulos */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
            <h2 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4">Módulos Activos (para {profile.name.split(' ')[0]})</h2>
            <div className="space-y-4">
                {(Object.keys(moduleLabels) as ModuleKey[]).map(key => (
                    <div key={key} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{moduleLabels[key]}</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input 
                                type="checkbox" 
                                checked={activeModules[key] || false} 
                                onChange={() => handleModuleToggle(key)}
                                className="sr-only peer" 
                            />
                            <div className="w-10 h-5 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all"></div>
                        </label>
                    </div>
                ))}
            </div>
        </div>
      </div>

      {/* Selector de Avatar Modal (Bottom Sheet Style) */}
      {isAvatarPickerOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] flex items-end justify-center p-4" onClick={() => setIsAvatarPickerOpen(false)}>
              <div className="bg-white dark:bg-gray-900 w-full max-w-md rounded-t-3xl p-6 animate-in slide-in-from-bottom duration-300" onClick={e => e.stopPropagation()}>
                  <div className="w-12 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-6"></div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Cambiar Foto de Perfil</h3>
                  
                  <div className="space-y-6">
                      {/* Botón de subida dispositivo */}
                      <button 
                        onClick={() => fileInputRef.current?.click()}
                        className="w-full p-4 bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-200 dark:border-blue-800 rounded-2xl flex items-center justify-center space-x-3 text-blue-600 dark:text-blue-400 font-bold active:scale-[0.98] transition-all"
                      >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                          <span>Subir desde el dispositivo</span>
                      </button>
                      <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="image/*" className="hidden" />

                      {/* Lista de avatares de la app */}
                      <div>
                          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4">Avatares de la App</p>
                          <div className="grid grid-cols-4 gap-3 max-h-[250px] overflow-y-auto pr-2 scrollbar-hide">
                              {APP_AVATARS.map((url, i) => (
                                  <button 
                                    key={i} 
                                    onClick={() => selectAppAvatar(url)}
                                    className={`relative rounded-xl overflow-hidden border-2 transition-all active:scale-90 ${profile.avatarUrl === url ? 'border-blue-500 scale-105 shadow-md' : 'border-gray-100 dark:border-gray-800'}`}
                                  >
                                      <img src={url} className="w-full h-full object-cover" alt={`Avatar ${i}`} />
                                      {profile.avatarUrl === url && (
                                          <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
                                              <div className="bg-white rounded-full p-0.5"><svg className="w-3 h-3 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg></div>
                                          </div>
                                      )}
                                  </button>
                              ))}
                          </div>
                      </div>

                      <button 
                        onClick={() => setIsAvatarPickerOpen(false)}
                        className="w-full py-3 bg-gray-100 dark:bg-gray-800 rounded-xl font-bold text-gray-500 uppercase text-xs"
                      >
                          Cerrar
                      </button>
                  </div>
              </div>
          </div>
      )}

      {isChildModalOpen && (
          <ItemFormModal
            item={null}
            type="profiles"
            title="Nuevo Hijo/a"
            onClose={() => setIsChildModalOpen(false)}
            onSave={(data) => {
                const newId = `child-${Date.now()}`;
                const newChild: StudentProfile = { 
                    ...data, 
                    id: newId,
                    activeModules: { subjects: true, exams: true, menu: true, events: true, dinner: true, contacts: true }
                };
                setProfiles(prev => [...prev, newChild]);
                setActiveProfileId(newId);
                setIsChildModalOpen(false);
            }}
          />
      )}
    </div>
  );
};

export default ProfilePage;
