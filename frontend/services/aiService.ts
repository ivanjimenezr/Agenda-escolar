
import { GoogleGenAI, Type } from "@google/genai";

const getAIClient = () => {
  return new GoogleGenAI({ apiKey: process.env.API_KEY });
};

export const aiService = {
  /**
   * Sugiere una cena para un día basada en lo que el niño comió en el colegio.
   */
  async suggestDinner(mainCourse: string, allergies: string[], excludedFoods: string[]) {
    const ai = getAIClient();
    const allergiesTxt = allergies.length > 0 ? `EVITA estrictamente: ${allergies.join(', ')}.` : '';
    const exclusionsTxt = excludedFoods.length > 0 ? `NO incluyas estos ingredientes: ${excludedFoods.join(', ')}.` : '';

    const prompt = `Sugiere una cena para hoy considerando que para comer hubo: ${mainCourse || 'comida variada'}. 
    RESTRICCIONES: ${allergiesTxt} ${exclusionsTxt}
    Responde en JSON con el campo "meal".`;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: { 
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.OBJECT,
          properties: { meal: { type: Type.STRING } },
          required: ['meal']
        }
      }
    });

    return response.text ? JSON.parse(response.text) : null;
  },

  /**
   * Genera un plan de cenas semanal o diario.
   */
  async generateDinnerPlan(type: 'today' | 'week', menuData: any, allergies: string[], excludedFoods: string[]) {
    const ai = getAIClient();
    const allergiesTxt = allergies.length > 0 ? `ALERGIAS: ${allergies.join(', ')}.` : '';
    const exclusionsTxt = excludedFoods.length > 0 ? `EXCLUSIONES: ${excludedFoods.join(', ')}.` : '';

    const prompt = `Sugiere ${type === 'today' ? 'una cena para hoy' : 'cenas para los próximos 5 días'} basándote en este menú escolar: ${JSON.stringify(menuData)}. 
    RESTRICCIONES: ${allergiesTxt} ${exclusionsTxt}
    Responde estrictamente en un array JSON con objetos que tengan "date" (YYYY-MM-DD) y "meal" (string).`;

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

    return response.text ? JSON.parse(response.text) : [];
  },

  /**
   * Genera una lista de la compra organizada por categorías.
   */
  async generateShoppingList(meals: string[]) {
    const ai = getAIClient();
    const prompt = `Crea una lista de la compra organizada por categorías para estas cenas: ${meals.join(', ')}. Responde solo JSON.`;
    
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

    return response.text ? JSON.parse(response.text) : [];
  }
};
