
import React, { useState } from 'react';
import type { Subject, Exam, MenuItem, SchoolEvent, ActiveModules, ModuleKey, Center, Contact } from '../types';
import { PlusIcon, TrashIcon, PencilIcon } from '../components/icons';
import ItemFormModal from '../components/ItemFormModal';
import ConfirmDialog from '../components/ConfirmDialog';
import { createMenu, updateMenu, deleteMenu, upsertMenu } from '../services/menuService';
import { deleteSubject } from '../services/subjectService';
import { createExam, updateExam, deleteExam } from '../services/examService';
import { transformMenuForCreate, transformMenuForUpdate } from '../utils/dataTransformers';

type Manageable = Exclude<ModuleKey, 'dinner'> | 'centers' | 'contacts';
type Item = Subject | Exam | MenuItem | SchoolEvent | Center | Contact;

interface ManagePageProps {
  activeProfileId: string;
  subjects: Subject[];
  reloadSubjects: () => void;
  exams: Exam[];
  setExams: (val: any) => void;
  reloadExams: () => void;
  menu: MenuItem[];
  setMenu: React.Dispatch<React.SetStateAction<MenuItem[]>>;
  events: SchoolEvent[];
  setEvents: React.Dispatch<React.SetStateAction<SchoolEvent[]>>;
  centers: Center[];
  setCenters: React.Dispatch<React.SetStateAction<Center[]>>;
  contacts: Contact[];
  setContacts: React.Dispatch<React.SetStateAction<Contact[]>>;
  activeModules: ActiveModules;
  reloadMenus?: () => Promise<void>;
}

const ManagePage: React.FC<ManagePageProps> = ({
  activeProfileId, subjects, reloadSubjects, exams, setExams, reloadExams, menu, setMenu, events, setEvents,
  centers, setCenters, contacts, setContacts, activeModules, reloadMenus,
}) => {
  const dataMap = {
    subjects: { title: 'Clases', data: subjects },
    exams: { title: 'Exámenes', data: exams, setData: setExams },
    menu: { title: 'Comedor', data: menu, setData: setMenu },
    events: { title: 'Eventos', data: events, setData: setEvents },
    contacts: { title: 'Directorio', data: contacts, setData: setContacts },
    centers: { title: 'Centros', data: centers, setData: setCenters },
  };

  const availableTabs: Manageable[] = ['subjects', 'exams', 'menu', 'events', 'contacts', 'centers'].filter(key => {
      if (key === 'centers' || key === 'contacts') return activeModules.contacts;
      return activeModules[key as keyof ActiveModules];
  }) as Manageable[];

  const [activeTab, setActiveTab] = useState<Manageable>(availableTabs[0] || 'subjects');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [showConfirmOverwrite, setShowConfirmOverwrite] = useState(false);
  const [pendingMenuData, setPendingMenuData] = useState<any>(null);

  // Debug: watch state changes
  React.useEffect(() => {
    console.log('[ManagePage] showConfirmOverwrite changed to:', showConfirmOverwrite);
    console.log('[ManagePage] pendingMenuData:', pendingMenuData);
  }, [showConfirmOverwrite, pendingMenuData]);

  const openModal = (item: Item | null = null) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleConfirmOverwrite = async () => {
    if (!pendingMenuData) return;

    try {
      await upsertMenu(pendingMenuData);
      if (reloadMenus) await reloadMenus();
      setShowConfirmOverwrite(false);
      setPendingMenuData(null);
      setIsModalOpen(false);
    } catch (error: any) {
      console.error('Error upserting menu:', error);
      alert(`Error al sobrescribir el menú: ${error.message || 'Error desconocido'}`);
      setShowConfirmOverwrite(false);
    }
  };

  const handleCancelOverwrite = () => {
    setShowConfirmOverwrite(false);
    setPendingMenuData(null);
    // Reopen the form modal so user can edit the date
    setIsModalOpen(true);
  };

  const handleDelete = async (item: Item, type: Manageable) => {
    if (!confirm('¿Borrar este elemento?')) return;

    if (type === 'subjects') {
      try {
        await deleteSubject(activeProfileId, item.id);
        reloadSubjects();
      } catch (error) {
        console.error('Error deleting subject:', error);
        alert('Error al eliminar la asignatura');
      }
    } else if (type === 'exams') {
      try {
        await deleteExam(activeProfileId, item.id);
        reloadExams();
      } catch (error) {
        console.error('Error deleting exam:', error);
        alert('Error al eliminar el examen');
      }
    } else if (type === 'menu') {
      try {
        await deleteMenu(item.id);
        if (reloadMenus) await reloadMenus();
      } catch (error) {
        console.error('Error deleting menu:', error);
        alert('Error al eliminar el menú');
      }
    } else {
      // Other types still use local state
      dataMap[type].setData((prev: any[]) => (prev as any).filter((p: any) => p.id !== item.id));
    }
  };

  const handleSave = async (data: any) => {
    if (activeTab === 'exams') {
      try {
        const payload = {
          subject: data.subject,
          date: data.date,
          topic: data.topic,
          notes: data.notes || undefined
        };

        if (editingItem) {
          // Update existing exam
          await updateExam(activeProfileId, editingItem.id, payload);
        } else {
          // Create new exam
          await createExam(activeProfileId, payload);
        }

        reloadExams();
        setIsModalOpen(false);
      } catch (error: any) {
        console.error('Error saving exam:', error);
        let errorMessage = 'Error desconocido';

        if (error instanceof Error) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        } else if (error?.details) {
          errorMessage = JSON.stringify(error.details);
        } else if (error?.message) {
          errorMessage = String(error.message);
        }

        console.error('Full error details:', JSON.stringify(error, null, 2));
        alert(`Error al guardar el examen: ${errorMessage}`);
      }
    } else if (activeTab === 'menu') {
      try {
        // Debug: raw form data from modal
        console.debug('[ManagePage] raw menu form data:', data);

        const payload = editingItem
          ? transformMenuForUpdate(data)
          : transformMenuForCreate(data, activeProfileId);

        // Debug: transformed payload to be sent to backend
        console.debug('[ManagePage] transformed menu payload:', payload);

        if (editingItem) {
          // Update existing menu
          await updateMenu(editingItem.id, payload);
        } else {
          // Create new menu - try normal create first
          try {
            await createMenu(payload);
          } catch (createError: any) {
            console.error('[ManagePage] Create error caught:', createError);

            // Check if error is duplicate constraint violation
            // Check in multiple places: message, details.detail, details, error string
            const errorString = JSON.stringify(createError).toLowerCase();
            const messageString = (createError?.message || '').toLowerCase();
            const detailString = (createError?.details?.detail || '').toLowerCase();

            const isDuplicateError =
              messageString.includes('duplicate key') ||
              messageString.includes('unique constraint') ||
              messageString.includes('uniqueviolation') ||
              messageString.includes('already exists') ||
              messageString.includes('use update or upsert') ||
              detailString.includes('duplicate key') ||
              detailString.includes('unique constraint') ||
              detailString.includes('uniqueviolation') ||
              detailString.includes('already exists') ||
              errorString.includes('duplicate key') ||
              errorString.includes('unique constraint') ||
              errorString.includes('already exists') ||
              errorString.includes('unique_menu_per_student_per_date');

            console.log('[ManagePage] Is duplicate error?', isDuplicateError);
            console.log('[ManagePage] Error details:', {
              message: createError?.message,
              details: createError?.details,
              errorString: errorString.substring(0, 200)
            });

            if (isDuplicateError) {
              // Show confirmation dialog
              console.log('[ManagePage] ✅ SHOWING MODAL - Duplicate detected!');
              console.log('[ManagePage] Payload:', payload);
              console.log('[ManagePage] Setting pendingMenuData and showConfirmOverwrite...');
              console.log('[ManagePage] Closing ItemFormModal to show ConfirmDialog');
              setIsModalOpen(false); // Close the form modal so ConfirmDialog is visible
              setPendingMenuData(payload);
              setShowConfirmOverwrite(true);
              console.log('[ManagePage] State updated, returning early');
              return;
            } else {
              // Re-throw if it's a different error
              throw createError;
            }
          }
        }
        if (reloadMenus) await reloadMenus();
        setIsModalOpen(false);
      } catch (error: any) {
        console.error('Error saving menu:', error);

        // Extract error message properly
        let errorMessage = 'Error desconocido';

        if (error instanceof Error) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        } else if (error?.details) {
          errorMessage = JSON.stringify(error.details);
        } else if (error?.message) {
          errorMessage = String(error.message);
        }

        // Log full error for debugging
        console.error('Full error details:', JSON.stringify(error, null, 2));

        alert(`Error al guardar el menú: ${errorMessage}`);
      }
    } else {
      // Other types still use local state
      const setData = dataMap[activeTab].setData as any;
      if (editingItem) {
        setData((prev: any[]) => prev.map((i: any) => i.id === editingItem.id ? { ...i, ...data } : i));
      } else {
        setData((prev: any[]) => [...prev, {
          ...data,
          id: Date.now().toString(),
          studentId: (activeTab === 'subjects' || activeTab === 'exams') ? activeProfileId : undefined
        }]);
      }
      setIsModalOpen(false);
    }
  };

  return (
    <div className="p-5 pb-24 animate-in slide-in-from-right duration-500 bg-gray-50 dark:bg-gray-950 min-h-full">
      <h1 className="text-xl font-black mb-6 text-gray-900 dark:text-white">Gestión de Datos</h1>
      <div className="flex space-x-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        {availableTabs.map((key) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all whitespace-nowrap shadow-sm border ${
              activeTab === key ? 'bg-blue-600 text-white border-blue-600' : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-700'
            }`}
          >
            {dataMap[key].title.toUpperCase()}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {(dataMap[activeTab].data as Item[]).map(item => (
            <div key={item.id} className="bg-white dark:bg-gray-800 rounded-2xl p-4 flex justify-between items-center shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
                <ItemDisplay item={item} type={activeTab} centers={centers} />
                <div className="flex space-x-1">
                    <button onClick={() => openModal(item)} className="p-2 text-blue-500 bg-blue-50 dark:bg-blue-900/20 rounded-lg active:scale-95 transition-transform"><PencilIcon className="w-4 h-4" /></button>
                    <button onClick={() => handleDelete(item, activeTab)} className="p-2 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg active:scale-95 transition-transform"><TrashIcon className="w-4 h-4" /></button>
                </div>
            </div>
        ))}
        {(dataMap[activeTab].data as Item[]).length === 0 && (
            <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700">
                <p className="text-sm font-bold text-gray-400 dark:text-gray-500 italic">No hay registros aún</p>
                <button onClick={() => openModal()} className="mt-3 text-blue-600 dark:text-blue-400 text-xs font-bold uppercase tracking-widest">Añadir primero</button>
            </div>
        )}
      </div>
      <button onClick={() => openModal()} className="fixed bottom-20 right-6 bg-blue-600 text-white rounded-2xl p-4 shadow-xl active:scale-90 z-20 border-2 border-white dark:border-gray-800"><PlusIcon className="w-6 h-6" /></button>
      {isModalOpen && (
        <ItemFormModal
            item={editingItem}
            type={activeTab}
            centers={centers}
            onClose={() => setIsModalOpen(false)}
            onSave={(result) => {
                if (activeTab === 'subjects') {
                    // Subject already saved to backend by ItemFormModal, just reload
                    reloadSubjects();
                    setIsModalOpen(false);
                } else if (activeTab === 'menu') {
                    // Existing menu saving logic starts here
                    try {
                        // Debug: raw form data from modal
                        console.debug('[ManagePage] raw menu form data:', result);

                        const payload = editingItem
                            ? transformMenuForUpdate(result)
                            : transformMenuForCreate(result, activeProfileId);

                        // Debug: transformed payload to be sent to backend
                        console.debug('[ManagePage] transformed menu payload:', payload);

                        const saveMenu = async () => {
                            if (editingItem) {
                                // Update existing menu
                                await updateMenu(editingItem.id, payload);
                            } else {
                                // Create new menu - try normal create first
                                try {
                                    await createMenu(payload);
                                } catch (createError: any) {
                                    console.error('[ManagePage] Create error caught:', createError);

                                    // Check if error is duplicate constraint violation
                                    const errorString = JSON.stringify(createError).toLowerCase();
                                    const messageString = (createError?.message || '').toLowerCase();
                                    const detailString = (createError?.details?.detail || '').toLowerCase();

                                    const isDuplicateError =
                                        messageString.includes('duplicate key') ||
                                        messageString.includes('unique constraint') ||
                                        messageString.includes('uniqueviolation') ||
                                        messageString.includes('already exists') ||
                                        messageString.includes('use update or upsert') ||
                                        detailString.includes('duplicate key') ||
                                        detailString.includes('unique constraint') ||
                                        detailString.includes('uniqueviolation') ||
                                        detailString.includes('already exists') ||
                                        errorString.includes('duplicate key') ||
                                        errorString.includes('unique constraint') ||
                                        errorString.includes('already exists') ||
                                        errorString.includes('unique_menu_per_student_per_date');

                                    console.log('[ManagePage] Is duplicate error?', isDuplicateError);
                                    console.log('[ManagePage] Error details:', {
                                        message: createError?.message,
                                        details: createError?.details,
                                        errorString: errorString.substring(0, 200)
                                    });

                                    if (isDuplicateError) {
                                        // Show confirmation dialog
                                        console.log('[ManagePage] ✅ SHOWING MODAL - Duplicate detected!');
                                        console.log('[ManagePage] Payload:', payload);
                                        console.log('[ManagePage] Setting pendingMenuData and showConfirmOverwrite...');
                                        console.log('[ManagePage] Closing ItemFormModal to show ConfirmDialog');
                                        setIsModalOpen(false); // Close the form modal so ConfirmDialog is visible
                                        setPendingMenuData(payload);
                                        setShowConfirmOverwrite(true);
                                        console.log('[ManagePage] State updated, returning early');
                                        return;
                                    } else {
                                        // Re-throw if it's a different error
                                        throw createError;
                                    }
                                }
                            }
                            if (reloadMenus) await reloadMenus();
                            setIsModalOpen(false);
                        };
                        saveMenu(); // Call the async function
                    } catch (error: any) {
                        console.error('Error saving menu:', error);

                        // Extract error message properly
                        let errorMessage = 'Error desconocido';

                        if (error instanceof Error) {
                            errorMessage = error.message;
                        } else if (typeof error === 'string') {
                            errorMessage = error;
                        } else if (error?.details) {
                            errorMessage = JSON.stringify(error.details);
                        } else if (error?.message) {
                            errorMessage = String(error.message);
                        }

                        // Log full error for debugging
                        console.error('Full error details:', JSON.stringify(error, null, 2));

                        alert(`Error al guardar el menú: ${errorMessage}`);
                    }
                    // Existing menu saving logic ends here
                } else {
                    // Other types still use local state for now
                    const setData = dataMap[activeTab].setData as any;
                    if (editingItem) {
                        setData((prev: any[]) => prev.map((i: any) => i.id === editingItem.id ? { ...i, ...result } : i));
                    } else {
                        setData((prev: any[]) => [...prev, {
                            ...result,
                            id: Date.now().toString(),
                            studentId: (activeTab === 'exams') ? activeProfileId : undefined // exams still need studentId for local state creation
                        }]);
                    }
                    setIsModalOpen(false);
                }
            }}
            title={dataMap[activeTab].title}
            studentId={activeProfileId}
        />
      )}

      <ConfirmDialog
        isOpen={showConfirmOverwrite}
        title="Menú duplicado"
        message={`Ya existe un menú para la fecha ${pendingMenuData?.date || ''}. ¿Deseas sobrescribir el menú existente?`}
        confirmText="Sobrescribir"
        cancelText="Cancelar"
        onConfirm={handleConfirmOverwrite}
        onCancel={handleCancelOverwrite}
        type="warning"
      />
    </div>
  );
};

const ItemDisplay: React.FC<{item: Item, type: Manageable, centers: Center[]}> = ({ item, type, centers }) => {
    switch(type) {
        case 'subjects':
            const s = item as Subject;
            return (
              <div>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{s.name}</p>
                <p className={`text-[10px] font-bold uppercase ${s.type === 'extraescolar' ? 'text-purple-600 dark:text-purple-400' : 'text-blue-600 dark:text-blue-400'}`}>
                  {s.days?.map(d => d.substring(0,3)).join(', ')} • {s.time} • {s.type}
                </p>
              </div>
            );
        case 'exams':
            const e = item as Exam;
            return (
              <div className="flex-1 mr-4">
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{e.subject}</p>
                <p className="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-tighter">{e.date} • {e.topic}</p>
              </div>
            );
        case 'menu':
            const m = item as MenuItem;
            return (
              <div>
                <p className="text-[10px] font-bold text-orange-600 dark:text-orange-400 uppercase mb-0.5">{m.date}</p>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{m.mainCourse}</p>
                <p className="text-[10px] text-gray-500 dark:text-gray-400">Postre: {m.dessert}</p>
              </div>
            );
        case 'events':
            const ev = item as SchoolEvent;
            return (
              <div>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{ev.name}</p>
                <p className="text-[10px] text-amber-600 dark:text-amber-400 font-bold uppercase tracking-tighter">{ev.date} • {ev.type}</p>
              </div>
            );
        case 'centers':
            const c = item as Center;
            return <div><p className="font-bold text-sm text-gray-900 dark:text-gray-100">{c.name}</p></div>;
        case 'contacts':
            const ct = item as Contact;
            const centerName = centers.find(center => center.id === ct.centerId)?.name || 'Sin centro';
            return (
              <div>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{ct.name}</p>
                <p className="text-[10px] text-gray-500 dark:text-gray-400 font-bold uppercase tracking-tighter">{centerName} • {ct.phone}</p>
              </div>
            );
        default: return null;
    }
}
export default ManagePage;
