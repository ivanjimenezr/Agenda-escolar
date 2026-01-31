
import React, { useState, useEffect } from 'react';
import type { DinnerItem, MenuItem, StudentProfile } from '../types';
import { SparklesIcon, ShoppingCartIcon, TrashIcon, MoonIcon } from '../components/icons';
import { generateDinners, getDinners, deleteDinner as deleteDinnerAPI, generateShoppingList } from '../services/dinnerService';

interface DinnersPageProps {
  dinners: DinnerItem[];
  setDinners: React.Dispatch<React.SetStateAction<DinnerItem[]>>;
  menu: MenuItem[];
  profile: StudentProfile;
}

const ShoppingListModal: React.FC<{ list: { category: string, items: string[] }[], onClose: () => void }> = ({ list, onClose }) => (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div className="bg-white dark:bg-gray-900 rounded-t-3xl sm:rounded-2xl w-full max-w-md max-h-[80vh] overflow-hidden flex flex-col shadow-2xl animate-in slide-in-from-bottom duration-300">
            <div className="p-5 border-b dark:border-gray-800 flex justify-between items-center bg-indigo-600 text-white">
                <div className="flex items-center">
                    <ShoppingCartIcon className="w-5 h-5 mr-2" />
                    <h2 className="text-lg font-bold uppercase tracking-tight">Lista de Compra</h2>
                </div>
                <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 transition-colors font-bold">✕</button>
            </div>
            <div className="flex-grow overflow-y-auto p-5 space-y-6">
                {list.map((cat, idx) => (
                    <div key={idx}>
                        <h3 className="font-bold text-[10px] uppercase text-indigo-500 mb-2 tracking-widest">{cat.category}</h3>
                        <div className="space-y-2">
                            {cat.items.map((item, i) => (
                                <label key={i} className="flex items-center p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 shadow-sm">
                                    <input type="checkbox" className="mr-3 h-5 w-5 rounded-lg border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                                    <span className="text-gray-900 dark:text-gray-100 text-sm font-semibold">{item}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
            <div className="p-5 bg-gray-50 dark:bg-gray-800 border-t dark:border-gray-700">
                <button onClick={onClose} className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-sm shadow-lg active:scale-95 transition-all">FINALIZAR COMPRA</button>
            </div>
        </div>
    </div>
);

const DinnersPage: React.FC<DinnersPageProps> = ({ dinners, setDinners, menu, profile }) => {
    const [generating, setGenerating] = useState(false);
    const [shoppingList, setShoppingList] = useState<{ category: string, items: string[] }[] | null>(null);
    const [loadingList, setLoadingList] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load dinners from backend on mount
    useEffect(() => {
        const loadDinners = async () => {
            try {
                const backendDinners = await getDinners(profile.id);
                // Transform backend format to frontend format
                const transformedDinners = backendDinners.map(d => ({
                    id: d.id,
                    studentId: d.student_id,
                    date: d.date,
                    meal: d.meal,
                    ingredients: d.ingredients
                }));
                setDinners(transformedDinners);
            } catch (e) {
                console.error('Error loading dinners:', e);
            }
        };

        if (profile?.id) {
            loadDinners();
        }
    }, [profile?.id]);

    const generateAI = async (type: 'today' | 'week') => {
        setGenerating(true);
        setError(null);
        try {
            const todayISO = new Date().toISOString().split('T')[0];

            // Call backend to generate dinners with AI
            const generatedDinners = await generateDinners(profile.id, {
                type: type,
                target_date: type === 'today' ? todayISO : undefined
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

                // Update state with new dinners (replacing existing ones for the same dates)
                setDinners(prev => {
                    const filtered = prev.filter(p =>
                        !transformedDinners.some(nd => nd.date === p.date)
                    );
                    return [...filtered, ...transformedDinners].sort((a, b) =>
                        a.date.localeCompare(b.date)
                    );
                });
            }
        } catch (e: any) {
            console.error('Error generating dinners:', e);
            const errorMsg = e.message || 'Error al conectar con la IA. Revisa tu conexión.';
            setError(errorMsg);
            alert(errorMsg);
        } finally {
            setGenerating(false);
        }
    };

    const fetchShoppingList = async (scope: 'today' | 'week') => {
        setLoadingList(true);
        setError(null);
        try {
            const todayISO = new Date().toISOString().split('T')[0];

            // Check if there are dinners for the scope
            const targetDinners = scope === 'today'
                ? dinners.filter(d => d.date === todayISO)
                : dinners;

            if (targetDinners.length === 0) {
                alert('No hay cenas planificadas para generar la lista.');
                return;
            }

            // Call backend to generate shopping list
            const response = await generateShoppingList(profile.id, { scope });

            if (response && response.categories) {
                setShoppingList(response.categories);
            }
        } catch (e: any) {
            console.error('Error generating shopping list:', e);
            const errorMsg = e.message || 'Error al generar la lista de compra.';
            setError(errorMsg);
            alert(errorMsg);
        } finally {
            setLoadingList(false);
        }
    };

    const handleDeleteDinner = async (dinnerId: string) => {
        try {
            await deleteDinnerAPI(profile.id, dinnerId);
            setDinners(prev => prev.filter(d => d.id !== dinnerId));
        } catch (e: any) {
            console.error('Error deleting dinner:', e);
            alert('Error al eliminar la cena.');
        }
    };

    return (
        <div className="p-5 pb-24 animate-in slide-in-from-bottom duration-500 bg-gray-50 dark:bg-gray-950 min-h-full">
            <header className="mb-8">
                <h1 className="text-2xl font-black text-gray-900 dark:text-white flex items-center">
                    <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/40 rounded-xl flex items-center justify-center mr-3">
                        <MoonIcon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    Plan de Cenas
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium mt-1">Sugerencias inteligentes para {profile.name.split(' ')[0]}</p>
            </header>

            <div className="grid grid-cols-2 gap-3 mb-8">
                <button onClick={() => generateAI('today')} disabled={generating} className="p-4 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-indigo-900/50 flex flex-col items-center justify-center space-y-2 active:scale-95 transition-all disabled:opacity-50 shadow-sm">
                    <SparklesIcon className="w-6 h-6 text-indigo-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-indigo-600 dark:text-indigo-400">Cena Hoy</span>
                </button>
                <button onClick={() => generateAI('week')} disabled={generating} className="p-4 bg-indigo-600 rounded-2xl flex flex-col items-center justify-center space-y-2 shadow-lg active:scale-95 transition-all disabled:opacity-50">
                    <SparklesIcon className="w-6 h-6 text-white" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-white">Semana Completa</span>
                </button>
            </div>

            <div className="mb-8">
                <p className="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-3 ml-1">Lista de la Compra</p>
                <div className="flex space-x-2">
                    <button onClick={() => fetchShoppingList('today')} disabled={loadingList} className="flex-1 py-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 text-xs font-black text-gray-600 dark:text-gray-300 shadow-sm active:bg-gray-50">
                        {loadingList ? 'PROCESANDO...' : 'COMPRA HOY'}
                    </button>
                    <button onClick={() => fetchShoppingList('week')} disabled={loadingList} className="flex-1 py-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 text-xs font-black text-gray-600 dark:text-gray-300 shadow-sm active:bg-gray-50">
                        {loadingList ? 'PROCESANDO...' : 'COMPRA SEMANAL'}
                    </button>
                </div>
            </div>

            <div>
                <p className="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-3 ml-1">Próximas Cenas Planificadas</p>
                <div className="space-y-3">
                    {dinners.length > 0 ? dinners.map(d => (
                        <div key={d.id} className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center justify-between transition-colors">
                            <div className="flex-grow">
                                <p className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">{d.date}</p>
                                <p className="text-sm font-bold text-gray-900 dark:text-gray-100 italic mt-0.5">"{d.meal}"</p>
                            </div>
                            <button onClick={() => handleDeleteDinner(d.id)} className="p-2 text-red-400 hover:text-red-600 active:scale-90 transition-all"><TrashIcon className="w-5 h-5" /></button>
                        </div>
                    )) : (
                        <div className="text-center py-12 bg-white dark:bg-gray-800/40 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700">
                            <MoonIcon className="w-10 h-10 mx-auto text-gray-300 dark:text-gray-600 mb-2" />
                            <p className="text-sm text-gray-400 font-bold italic">No hay cenas planificadas</p>
                        </div>
                    )}
                </div>
            </div>

            {shoppingList && <ShoppingListModal list={shoppingList} onClose={() => setShoppingList(null)} />}
            {generating && (
                <div className="fixed inset-0 bg-indigo-600/95 backdrop-blur-xl z-[100] flex flex-col items-center justify-center text-white p-8 animate-in fade-in duration-300">
                    <div className="w-20 h-20 border-4 border-white border-t-transparent rounded-full animate-spin mb-8 shadow-2xl"></div>
                    <h2 className="text-2xl font-black mb-3 tracking-tight">Creando tu menú...</h2>
                    <p className="text-indigo-100 text-center text-sm font-bold max-w-xs leading-relaxed opacity-80">Estamos analizando el menú escolar y las restricciones dietéticas para sugerir las mejores cenas.</p>
                </div>
            )}
        </div>
    );
};
export default DinnersPage;
