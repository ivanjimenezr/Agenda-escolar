"""
Gemini AI Service

Service for integrating with Google's Gemini AI for dinner suggestions
"""

import json
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from src.infrastructure.config import settings


class GeminiService:
    """Service for Gemini AI integration"""

    def __init__(self):
        """Initialize Gemini AI client"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def _build_restrictions_text(self, allergies: List[str], excluded_foods: List[str]) -> str:
        """Build restrictions text for prompts"""
        restrictions = []

        if allergies:
            allergies_formatted = [a.lower() for a in allergies]
            restrictions.append(
                f"⚠️ RESTRICCIONES CRÍTICAS - ALERGIAS: {', '.join(allergies_formatted)}. "
                "NUNCA incluir estos ingredientes bajo ninguna circunstancia."
            )

        if excluded_foods:
            excluded_formatted = [f.lower() for f in excluded_foods]
            restrictions.append(f"❌ NO incluir estos ingredientes: {', '.join(excluded_formatted)}.")

        return " ".join(restrictions) if restrictions else ""

    async def suggest_dinner_for_day(
        self,
        target_date: date,
        school_menu: Optional[Dict[str, Any]],
        week_menus: List[Dict[str, Any]],
        allergies: List[str],
        excluded_foods: List[str],
    ) -> Dict[str, Any]:
        """
        Suggest a dinner for a specific day

        Args:
            target_date: The date for the dinner
            school_menu: School menu for that specific day (None if weekend/holiday)
            week_menus: School menus from the current week for context
            allergies: List of allergies to avoid
            excluded_foods: List of foods to exclude

        Returns:
            Dict with 'meal' and 'ingredients' keys
        """
        restrictions = self._build_restrictions_text(allergies, excluded_foods)

        # Build context about the week
        week_context = ""
        if week_menus:
            week_dishes = []
            for menu in week_menus:
                dishes = []
                if menu.get("first_course"):
                    dishes.append(menu["first_course"])
                if menu.get("second_course"):
                    dishes.append(menu["second_course"])
                if dishes:
                    week_dishes.append(f"{menu['date']}: {', '.join(dishes)}")

            if week_dishes:
                week_context = f"\n\n📅 MENÚS DE LA SEMANA (para equilibrio nutricional):\n" + "\n".join(week_dishes)

        # Build day context
        if school_menu:
            day_menu = []
            if school_menu.get("first_course"):
                day_menu.append(f"Primer plato: {school_menu['first_course']}")
            if school_menu.get("second_course"):
                day_menu.append(f"Segundo plato: {school_menu['second_course']}")
            if school_menu.get("side_dish"):
                day_menu.append(f"Guarnición: {school_menu['side_dish']}")
            if school_menu.get("dessert"):
                day_menu.append(f"Postre: {school_menu['dessert']}")

            day_context = f"🍽️ MENÚ ESCOLAR DEL DÍA ({target_date}):\n" + "\n".join(day_menu)
            prompt_instruction = "Sugiere una cena COMPLEMENTARIA Y EQUILIBRADA que complete nutricionalmente lo que el niño comió en el colegio."
        else:
            day_context = f"🏠 DÍA SIN MENÚ ESCOLAR ({target_date}) - Fin de semana o festivo"
            prompt_instruction = "Sugiere una cena COMPLETA Y EQUILIBRADA. Analiza los menús de la semana para evitar repetir ingredientes principales y mantener variedad nutricional."

        prompt = f"""Eres un nutricionista experto especializado en alimentación infantil.

{day_context}
{week_context}

{restrictions}

🎯 TAREA:
{prompt_instruction}

📋 REQUISITOS:
- La cena debe ser saludable, equilibrada y apropiada para niños
- Incluir proteínas, verduras/vegetales y carbohidratos en proporciones adecuadas
- Evitar repetir los mismos ingredientes principales del menú escolar
- Considerar el equilibrio nutricional de toda la semana
- Respetar ESTRICTAMENTE las restricciones alimentarias
- Proponer un plato real y apetecible para un niño

📤 FORMATO DE RESPUESTA:
Responde SOLO con un objeto JSON válido con esta estructura exacta:
{{
    "meal": "Nombre completo del plato sugerido (ej: 'Pechuga de pollo a la plancha con ensalada mixta')",
    "ingredients": ["ingrediente1", "ingrediente2", "ingrediente3", ...]
}}

IMPORTANTE: No incluyas explicaciones adicionales, solo el JSON."""

        try:
            response = self.model.generate_content(prompt)

            # Parse JSON from response
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)

            return {"meal": result.get("meal", ""), "ingredients": result.get("ingredients", [])}

        except Exception as e:
            raise Exception(f"Error generating dinner suggestion: {str(e)}")

    async def suggest_dinners_for_week(
        self,
        start_date: date,
        days: int,
        school_menus: List[Dict[str, Any]],
        allergies: List[str],
        excluded_foods: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Suggest dinners for multiple days

        Args:
            start_date: Starting date
            days: Number of days to generate
            school_menus: School menus for the period (may be empty for some dates)
            allergies: List of allergies to avoid
            excluded_foods: List of foods to exclude

        Returns:
            List of dicts with 'date', 'meal', and 'ingredients' keys
        """
        restrictions = self._build_restrictions_text(allergies, excluded_foods)

        # Build menus context
        menus_by_date = {menu["date"]: menu for menu in school_menus}

        # Build week planning context
        days_info = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            day_name = current_date.strftime("%A")  # Monday, Tuesday, etc.

            if date_str in menus_by_date:
                menu = menus_by_date[date_str]
                dishes = []
                if menu.get("first_course"):
                    dishes.append(menu["first_course"])
                if menu.get("second_course"):
                    dishes.append(menu["second_course"])

                days_info.append(f"📅 {date_str} ({day_name}): MENÚ ESCOLAR - {', '.join(dishes)}")
            else:
                days_info.append(f"📅 {date_str} ({day_name}): SIN MENÚ ESCOLAR (fin de semana/festivo)")

        days_context = "\n".join(days_info)

        prompt = f"""Eres un nutricionista experto especializado en planificación de menús infantiles semanales.

🗓️ PLANIFICACIÓN DE CENAS PARA {days} DÍAS:
{days_context}

{restrictions}

🎯 TAREA:
Crea un plan de cenas para estos {days} días que:
1. COMPLEMENTE el menú escolar cuando existe
2. SEA COMPLETO Y EQUILIBRADO cuando no hay menú escolar
3. VARÍE los ingredientes principales entre días
4. MANTENGA EQUILIBRIO NUTRICIONAL durante toda la semana
5. SEA APETECIBLE para niños

📋 REQUISITOS:
- Cada cena debe incluir proteínas, verduras y carbohidratos
- Máxima variedad de ingredientes entre días
- Respetar ESTRICTAMENTE las restricciones alimentarias
- Platos reales y prácticos de preparar
- Considerar que los días con menú escolar la cena debe ser COMPLEMENTARIA
- Los días sin menú escolar la cena debe ser MÁS COMPLETA

📤 FORMATO DE RESPUESTA:
Responde SOLO con un array JSON válido con esta estructura exacta:
[
    {{
        "date": "YYYY-MM-DD",
        "meal": "Nombre del plato",
        "ingredients": ["ingrediente1", "ingrediente2", ...]
    }},
    ...
]

IMPORTANTE: Debe haber exactamente {days} cenas en el array, una por cada día. No incluyas explicaciones, solo el JSON."""

        try:
            response = self.model.generate_content(prompt)

            # Parse JSON from response
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)

            return result

        except Exception as e:
            raise Exception(f"Error generating weekly dinner plan: {str(e)}")

    async def generate_shopping_list(self, dinners: List[Dict[str, Any]], num_people: int = 4) -> List[Dict[str, Any]]:
        """
        Generate a categorized shopping list from dinner plans

        Args:
            dinners: List of dinner items with 'meal' and 'ingredients'
            num_people: Number of people (diners) for portion calculation

        Returns:
            List of categories with items
        """
        if not dinners:
            return []

        meals_text = "\n".join(
            [f"- {dinner['meal']}: {', '.join(dinner.get('ingredients', []))}" for dinner in dinners]
        )

        prompt = f"""Eres un asistente de compras experto especializado en planificación de cenas ligeras.

🛒 CENAS PLANIFICADAS:
{meals_text}

👥 NÚMERO DE COMENSALES: {num_people} personas

🎯 TAREA:
Crea una lista de la compra organizada por categorías con TODOS los ingredientes necesarios para CENAS LIGERAS.

📋 REQUISITOS IMPORTANTES:
- **CANTIDADES PARA CENAS LIGERAS**: Las porciones deben ser apropiadas para una cena, NO para comida principal
- Las cantidades deben ser para {num_people} personas
- Agrupar ingredientes por categoría (Carnes y Pescados, Verduras y Hortalizas, Frutas, Lácteos y Huevos, Despensa, Congelados, etc.)
- Eliminar duplicados y sumar cantidades de ingredientes repetidos
- Usar cantidades específicas y realistas (ej: "500g de pollo", "2 tomates", "1 litro de leche")
- Para cenas ligeras, reduce las cantidades en un 25-30% respecto a una comida principal
- Incluir ingredientes básicos necesarios (aceite, sal, especias básicas)
- Pensar en cantidades que se venden normalmente en supermercados

💡 EJEMPLO DE CANTIDADES LIGERAS (para 4 personas):
- Proteína: 400-500g (100-125g por persona)
- Verduras: 600-800g
- Carbohidratos: 300-400g (pasta, arroz, pan)

📤 FORMATO DE RESPUESTA:
Responde SOLO con un array JSON válido:
[
    {{
        "category": "Nombre de categoría",
        "items": ["cantidad + ingrediente", "cantidad + ingrediente", ...]
    }},
    ...
]

Ejemplo:
[
    {{
        "category": "Carnes y Pescados",
        "items": ["400g de pechuga de pollo", "300g de salmón fresco"]
    }},
    {{
        "category": "Verduras y Hortalizas",
        "items": ["4 tomates medianos", "1 lechuga", "2 pimientos rojos"]
    }}
]

IMPORTANTE: Solo el JSON, sin explicaciones adicionales. Las cantidades deben ser para CENAS LIGERAS."""

        try:
            response = self.model.generate_content(prompt)

            # Parse JSON from response
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)

            return result

        except Exception as e:
            raise Exception(f"Error generating shopping list: {str(e)}")
