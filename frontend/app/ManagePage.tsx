
import React, { useState } from 'react';
import type { Subject, Exam, MenuItem, SchoolEvent, ActiveModules, ModuleKey, Center, Contact } from '../types';
import { PlusIcon, TrashIcon, PencilIcon } from '../components/icons';
import ItemFormModal from '../components/ItemFormModal';

type Manageable = Exclude<ModuleKey, 'dinner'> | 'centers' | 'contacts';
type Item = Subject | Exam | MenuItem | SchoolEvent | Center | Contact;

interface ManagePageProps {
  activeProfileId: string;
  subjects: Subject[];
  setSubjects: (val: any) => void;
  exams: Exam[];
  setExams: (val: any) => void;
  menu: MenuItem[];
  setMenu: React.Dispatch<React.SetStateAction<MenuItem[]>>;
  events: SchoolEvent[];
  setEvents: React.Dispatch<React.SetStateAction<SchoolEvent[]>>;
  centers: Center[];
  setCenters: React.Dispatch<React.SetStateAction<Center[]>>;
  contacts: Contact[];
  setContacts: React.Dispatch<React.SetStateAction<Contact[]>>;
  activeModules: ActiveModules;
}

const ManagePage: React.FC<ManagePageProps> = ({
  activeProfileId, subjects, setSubjects, exams, setExams, menu, setMenu, events, setEvents, 
  centers, setCenters, contacts, setContacts, activeModules,
}) => {
  const dataMap = {
    subjects: { title: 'Clases', data: subjects, setData: setSubjects },
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

  const openModal = (item: Item | null = null) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  return (
    <div className="p-5 pb-24 animate-in slide-in-from-right duration-500">
      <h1 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">Gestión de Datos</h1>
      <div className="flex space-x-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        {availableTabs.map((key) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all whitespace-nowrap ${
              activeTab === key ? 'bg-blue-600 text-white shadow-sm' : 'bg-white dark:bg-gray-800 text-gray-500'
            }`}
          >
            {dataMap[key].title.toUpperCase()}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {(dataMap[activeTab].data as Item[]).map(item => (
            <div key={item.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 flex justify-between items-center shadow-sm border border-gray-100 dark:border-gray-700">
                <ItemDisplay item={item} type={activeTab} centers={centers} />
                <div className="flex space-x-1">
                    <button onClick={() => openModal(item)} className="p-2 text-blue-500 bg-blue-50 dark:bg-blue-900/20 rounded-lg"><PencilIcon className="w-4 h-4" /></button>
                    <button onClick={() => { if(confirm('¿Borrar?')) dataMap[activeTab].setData((prev: any[]) => (prev as any).filter((p: any) => p.id !== item.id)) }} className="p-2 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg"><TrashIcon className="w-4 h-4" /></button>
                </div>
            </div>
        ))}
      </div>
      <button onClick={() => openModal()} className="fixed bottom-20 right-6 bg-blue-600 text-white rounded-2xl p-4 shadow-lg active:scale-90 z-20"><PlusIcon className="w-6 h-6" /></button>
      {isModalOpen && (
        <ItemFormModal
            item={editingItem}
            type={activeTab}
            centers={centers}
            onClose={() => setIsModalOpen(false)}
            onSave={(data) => {
                const setData = dataMap[activeTab].setData as any;
                if (editingItem) {
                    setData((prev: any[]) => prev.map(i => i.id === editingItem.id ? { ...i, ...data } : i));
                } else {
                    setData((prev: any[]) => [...prev, { ...data, id: Date.now().toString(), studentId: (activeTab === 'subjects' || activeTab === 'exams') ? activeProfileId : undefined }]);
                }
                setIsModalOpen(false);
            }}
            title={dataMap[activeTab].title}
        />
      )}
    </div>
  );
};

const ItemDisplay: React.FC<{item: Item, type: Manageable, centers: Center[]}> = ({ item, type, centers }) => {
    switch(type) {
        case 'subjects':
            const s = item as Subject;
            return <div><p className="font-bold text-sm">{s.name}</p><p className={`text-[10px] font-bold uppercase ${s.type === 'extraescolar' ? 'text-purple-500' : 'text-blue-500'}`}>{s.days?.join(', ')} • {s.time}</p></div>;
        case 'exams':
            const e = item as Exam;
            return <div className="flex-1 mr-4"><p className="font-bold text-sm">{e.subject}</p><p className="text-[10px] text-red-500 font-bold uppercase">{e.date} • {e.topic}</p></div>;
        default: return null;
    }
}
export default ManagePage;
