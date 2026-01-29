import React, { useState } from 'react';
import type { DinnerItem, MenuItem, StudentProfile } from '../types';
import { SparklesIcon, ShoppingCartIcon, PlusIcon, TrashIcon, PencilIcon, MoonIcon } from '../components/icons';
import { GoogleGenAI, Type } from "@google/genai";

interface DinnersPageProps {
  dinners: DinnerItem[];
  setDinners: React.Dispatch<React.SetStateAction<DinnerItem[]>>;
  menu: MenuItem[];
  profile: StudentProfile;
}

const ShoppingListModal: React.FC<{ list: { category: string, items: string[] }[], onClose: () => void }> = ({ list, onClose }) => (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-md z-[60] flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div className="bg-white dark:bg-gray-900 rounded-t-3xl sm:rounded-2xl w-full max-w-md max-h-[80vh] overflow-hidden flex flex-col shadow-2xl animate-in slide-in-from-bottom duration-300">
            <div className="p-5 border-b dark:border-gray-800 flex justify-between items-center bg-indigo-600 text-white">
                <div className="flex items-center">
                    <ShoppingCartIcon className="w-5 h-5 mr-2" />
                    <h2 className="text-lg font-bold uppercase tracking-tight">Lista de Compra</h2>
                </div>
                <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 transition-colors">✕</button>
            </div>
            <div className="flex-grow overflow-y-auto p-5 space-y-6">
                {list.map((cat, idx) => (
                    <div key={idx}>
                        <h3 className="font-bold text-[10px] uppercase text-indigo-500 mb-2 tracking-widest">{cat.category}</h3>
                        <div className="space-y-1">
                            {cat.items.map((item, i) => (
                                <label key={i} className="flex items-center p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
                                    <input type="checkbox" className="mr-3 h-4 w-4 rounded border-gray-300 text-indigo-600" />
                                    <span className="text-gray-700 dark:text-gray-200 text-sm font-medium">{item}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
            <div className="p-5 bg-gray-50 dark:bg-gray-800/50 border-t dark:border-gray-800">
                <button onClick={onClose} className="w-full py-3 bg-indigo-600 text-white rounded-xl font-bold text-sm shadow-md active:scale-95">Finalizar</button>
            </div>
        </div>
    </div>
);

const DinnersPage: React.FC<DinnersPageProps> = ({ dinners, setDinners, menu, profile }) => {
    const [generating, setGenerating] = useState(false);
    const [shoppingList, setShoppingList] = useState<{ category: string, items: string[] }[] | null>(null);
    const [loadingList, setLoadingList] = useState(false);

    const generateAI = async (type: 'today' | 'week') => {
        setGenerating(true);
        try {
            const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
            const todayISO = new Date().toISOString().split('T')[0];
            const relevantMenu = type === 'today' 
                ? menu.find(m => m.date === todayISO) 
                : menu.slice(0, 5);
            
            const allergiesTxt = profile.allergies.length > 0 ? `EVITA estrictamente: ${profile.allergies.join(', ')}.` : '';
            const exclusionsTxt = profile.excludedFoods.length > 0 ? `NO incluyas bajo ningún concepto estos ingredientes: ${profile.excludedFoods.join(', ')}.` : '';

            const prompt = `Sugiere ${type === 'today' ? 'una cena para hoy' : 'cenas para los próximos 5 días'} basándote en que en el colegio comen esto: ${JSON.stringify(relevantMenu)}. 
            RESTRICCIONES IMPORTANTES: ${allergiesTxt} ${exclusionsTxt}
            Responde estrictamente en formato JSON con campos "date" (YYYY-MM-DD) y "meal" (string).`;

            const response = await ai.models.generateContent({
                model: 'gemini-3-flash-preview',
                contents: prompt,
                config: { 
                    responseMimeType: 'application/json',
                    responseSchema: {
                        type: Type.ARRAY,
                        items: {
                            type: Type.OBJECT,
                            properties: { date: { type: Type.STRING }, meal: { type: Type.STRING } },
                            required: ['date', 'meal']
                        }
                    }
                }
            });

            if (response.text) {
                const results = JSON.parse(response.text);
                setDinners(prev => {
                    const filtered = prev.filter(p => !results.some((r: any) => r.date === p.date));
                    return [...filtered, ...results.map((r: any) => ({ ...r, id: Math.random().toString(36).substr(2, 9), ingredients: [] }))].sort((a,b) => a.date.localeCompare(b.date));
                });
            }
        } catch (e) { console.error(e); } finally { setGenerating(false); }
    };

    const fetchShoppingList = async (scope: 'today' | 'week') => {
        setLoadingList(true);
        try {
            const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
            const todayISO = new Date().toISOString().split('T')[0];
            const targetDinners = scope === 'today' 
                ? dinners.filter(d => d.date === todayISO)
                : dinners;

            if (targetDinners.length === 0) {
                alert('No hay cenas planificadas para este periodo.');
                return;
            }

            const prompt = `Crea una lista de la compra organizada por categorías para estas cenas: ${targetDinners.map(d => d.meal).join(', ')}. Responde solo JSON.`;
            const response = await ai.models.generateContent({
                model: 'gemini-3-flash-preview',
                contents: prompt,
                config: {
                    responseMimeType: 'application/json',
                    responseSchema: {
                        type: Type.ARRAY,
                        items: {
                            type: Type.OBJECT,
                            properties: {
                                category: { type: Type.STRING },
                                items: { type: Type.ARRAY, items: { type: Type.STRING } }
                            },
                            required: ['category', 'items']
                        }
                    }
                }
            });
            if (response.text) setShoppingList(JSON.parse(response.text));
        } catch (e) { console.error(e); } finally { setLoadingList(false); }
    };

    return (
        <div className="p-5 pb-24 animate-in slide-in-from-bottom duration-500">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                    <MoonIcon className="w-7 h-7 mr-3 text-indigo-500" />
                    Plan de Cenas
                </h1>
                <p className="text-sm text-gray-500 font-medium">Gestiona la alimentación nocturna y compra</p>
            </header>

            {/* Acciones de IA */}
            <div className="grid grid-cols-2 gap-3 mb-8">
                <button 
                    onClick={() => generateAI('today')}
                    disabled={generating}
                    className="p-4 bg-white dark:bg-gray-800 rounded-2xl border-2 border-dashed border-indigo-200 dark:border-indigo-900 flex flex-col items-center justify-center space-y-2 active:scale-95 transition-all disabled:opacity-50"
                >
                    <SparklesIcon className="w-6 h-6 text-indigo-500" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">Cena Hoy</span>
                </button>
                <button 
                    onClick={() => generateAI('week')}
                    disabled={generating}
                    className="p-4 bg-indigo-600 rounded-2xl flex flex-col items-center justify-center space-y-2 shadow-lg active:scale-95 transition-all disabled:opacity-50"
                >
                    <SparklesIcon className="w-6 h-6 text-white" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-white">Semana Completa</span>
                </button>
            </div>

            {/* Listas de Compra */}
            <div className="mb-8">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3 ml-1">Lista de la Compra</p>
                <div className="flex space-x-2">
                    <button 
                        onClick={() => fetchShoppingList('today')}
                        disabled={loadingList}
                        className="flex-1 py-3 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 text-xs font-bold text-gray-600 dark:text-gray-300 flex items-center justify-center"
                    >
                        {loadingList ? '...' : 'COMPRA HOY'}
                    </button>
                    <button 
                        onClick={() => fetchShoppingList('week')}
                        disabled={loadingList}
                        className="flex-1 py-3 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 text-xs font-bold text-gray-600 dark:text-gray-300 flex items-center justify-center"
                    >
                        {loadingList ? '...' : 'COMPRA SEMANAL'}
                    </button>
                </div>
            </div>

            {/* Historial / Próximas */}
            <div>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3 ml-1">Próximas Cenas</p>
                <div className="space-y-3">
                    {dinners.length > 0 ? dinners.map(d => (
                        <div key={d.id} className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between">
                            <div className="flex-grow">
                                <p className="text-[10px] font-bold text-indigo-500 uppercase">{d.date}</p>
                                <p className="text-sm font-bold text-gray-800 dark:text-gray-100 italic">"{d.meal}"</p>
                            </div>
                            <button 
                                onClick={() => setDinners(prev => prev.filter(p => p.id !== d.id))}
                                className="p-2 text-red-400 hover:text-red-600"
                            >
                                <TrashIcon className="w-5 h-5" />
                            </button>
                        </div>
                    )) : (
                        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/40 rounded-3xl border-2 border-dashed border-gray-100 dark:border-gray-700">
                            <MoonIcon className="w-10 h-10 mx-auto text-gray-300 mb-2" />
                            <p className="text-sm text-gray-400 font-medium">No hay cenas planificadas</p>
                        </div>
                    )}
                </div>
            </div>

            {shoppingList && <ShoppingListModal list={shoppingList} onClose={() => setShoppingList(null)} />}
            
            {generating && (
                <div className="fixed inset-0 bg-indigo-600/90 backdrop-blur-md z-[100] flex flex-col items-center justify-center text-white p-8">
                    <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mb-6"></div>
                    <h2 className="text-2xl font-bold mb-2">Creando tu menú...</h2>
                    <p className="text-indigo-100 text-center text-sm font-medium">Estamos revisando el menú del cole, las alergias y tus gustos para sugerirte lo mejor.</p>
                </div>
            )}
        </div>
    );
};

export default DinnersPage;