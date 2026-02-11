/**
 * Helper para interceptar las llamadas a la API del backend
 * y devolver respuestas mock deterministas en los tests E2E.
 */
import { Page } from '@playwright/test';

// ---------- Datos mock reutilizables ----------

export const MOCK_USER = {
  id: 'user-e2e-001',
  email: 'test@e2e.com',
  name: 'Test User',
  is_active: true,
  email_verified: true,
  created_at: '2025-01-01T00:00:00Z',
};

export const MOCK_TOKEN = 'fake-jwt-token-e2e';

export const MOCK_STUDENT = {
  id: 'student-e2e-001',
  name: 'Alex García',
  school: 'Colegio Cervantes',
  grade: '5º Primaria',
  avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=e2e',
  allergies: [],
  excludedFoods: [],
  activeModules: {
    subjects: true,
    exams: true,
    menu: true,
    events: true,
    dinner: true,
    contacts: true,
  },
};

export const MOCK_SUBJECT = {
  id: 'subject-e2e-001',
  studentId: 'student-e2e-001',
  name: 'Matemáticas',
  days: ['Lunes'],
  time: '09:00',
  teacher: '',
  color: '#3B82F6',
  type: 'colegio' as const,
};

const DEFAULT_ACTIVE_MODULES = {
  subjects: true,
  exams: true,
  menu: true,
  events: true,
  dinner: true,
  contacts: true,
};

// ---------- Estado mutable para simular creaciones ----------

interface MockState {
  students: typeof MOCK_STUDENT[];
  subjects: typeof MOCK_SUBJECT[];
}

// ---------- Función principal ----------

/**
 * Intercepta todas las rutas de la API y devuelve respuestas mock.
 * El estado se puede mutar para simular creaciones (POST) dentro del test.
 */
export async function setupMockApi(page: Page, initialState?: Partial<MockState>) {
  const state: MockState = {
    students: initialState?.students ?? [],
    subjects: initialState?.subjects ?? [],
  };

  const API_PATTERN = '**/api/v1/**';

  await page.route(API_PATTERN, (route) => {
    const url = route.request().url();
    const method = route.request().method();

    // --- Auth ---
    if (url.includes('/api/v1/auth/register') && method === 'POST') {
      return route.fulfill({ status: 200, json: MOCK_USER });
    }

    if (url.includes('/api/v1/auth/login') && method === 'POST') {
      return route.fulfill({
        status: 200,
        json: {
          access_token: MOCK_TOKEN,
          token_type: 'bearer',
          user: MOCK_USER,
        },
      });
    }

    // --- Users ---
    if (url.includes('/api/v1/users/me') && method === 'GET') {
      return route.fulfill({ status: 200, json: MOCK_USER });
    }

    // --- Students ---
    if (url.match(/\/api\/v1\/students$/) && method === 'GET') {
      return route.fulfill({ status: 200, json: state.students });
    }

    if (url.match(/\/api\/v1\/students$/) && method === 'POST') {
      state.students.push(MOCK_STUDENT);
      return route.fulfill({ status: 201, json: MOCK_STUDENT });
    }

    // --- Active Modules ---
    if (url.includes('/active-modules') && method === 'GET') {
      return route.fulfill({ status: 200, json: DEFAULT_ACTIVE_MODULES });
    }

    // --- Subjects ---
    if (url.match(/\/students\/[^/]+\/subjects$/) && method === 'GET') {
      return route.fulfill({ status: 200, json: state.subjects });
    }

    if (url.match(/\/students\/[^/]+\/subjects/) && method === 'POST') {
      state.subjects.push(MOCK_SUBJECT);
      return route.fulfill({ status: 201, json: MOCK_SUBJECT });
    }

    // --- Exams ---
    if (url.includes('/exams') && method === 'GET') {
      return route.fulfill({ status: 200, json: [] });
    }

    // --- Menus ---
    if (url.includes('/menus') && method === 'GET') {
      return route.fulfill({ status: 200, json: [] });
    }

    // --- Dinners ---
    if (url.includes('/dinners') && method === 'GET') {
      return route.fulfill({ status: 200, json: [] });
    }

    // --- Events ---
    if (url.includes('/events') && method === 'GET') {
      return route.fulfill({ status: 200, json: [] });
    }

    // --- Fallback: devolver 200 vacío para cualquier GET no manejado ---
    if (method === 'GET') {
      return route.fulfill({ status: 200, json: [] });
    }

    // POST/PUT/DELETE no manejados → 200 genérico
    return route.fulfill({ status: 200, json: {} });
  });

  return state;
}

/**
 * Inyecta sesión autenticada en localStorage para saltar el login.
 */
export async function injectAuthSession(page: Page) {
  await page.addInitScript(
    ({ user, token }) => {
      localStorage.setItem('school-agenda-auth-v2', JSON.stringify(user));
      localStorage.setItem('auth-token', token);
    },
    { user: MOCK_USER, token: MOCK_TOKEN }
  );
}
