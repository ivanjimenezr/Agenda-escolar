import { test, expect } from '@playwright/test';
import { setupMockApi, injectAuthSession } from './helpers/mock-api';

test.describe('Flujo estudiante', () => {
  test.beforeEach(async ({ page }) => {
    // Inyectar sesión autenticada para saltar login
    await injectAuthSession(page);
  });

  test('crear perfil de estudiante y añadir asignatura', async ({ page }) => {
    // Arrancar sin estudiantes (estado vacío)
    await setupMockApi(page, { students: [], subjects: [] });

    await page.goto('/');

    // Sin perfiles → muestra pantalla de bienvenida con botón de crear
    await expect(page.getByText('Bienvenido a Agenda Escolar Pro')).toBeVisible({ timeout: 10_000 });
    await page.getByRole('button', { name: 'Crear Primer Perfil' }).click();

    // Se abre el modal de crear estudiante (auto-open al no tener perfiles)
    await expect(page.getByText('Añadir Estudiante')).toBeVisible({ timeout: 5_000 });

    // Rellenar formulario de estudiante
    await page.getByPlaceholder('Ej: Alex García').fill('Alex García');
    await page.getByPlaceholder('Ej: Colegio Cervantes').fill('Colegio Cervantes');
    await page.getByPlaceholder('Ej: 5º Primaria').fill('5º Primaria');

    // Guardar → mock POST devuelve student
    await page.getByRole('button', { name: 'Guardar' }).click();

    // Esperar a que se cargue el perfil (la app recarga estudiantes)
    // El mock ahora devuelve el estudiante creado en GET /students
    await expect(page.getByRole('heading', { name: 'Alex García' })).toBeVisible({ timeout: 10_000 });

    // Navegar a Gestionar
    await page.getByRole('button', { name: 'Gestionar' }).click();

    // Verificar que estamos en la página de gestión
    await expect(page.getByText('Gestión de Datos')).toBeVisible({ timeout: 5_000 });

    // Click en FAB (+) para añadir asignatura (tab por defecto es CLASES)
    await expect(page.getByText('CLASES')).toBeVisible();
    await page.locator('button.fixed').click();

    // Se abre el modal de crear asignatura
    await expect(page.getByPlaceholder('Ej: Matemáticas')).toBeVisible({ timeout: 5_000 });

    // Rellenar formulario de asignatura
    await page.getByPlaceholder('Ej: Matemáticas').fill('Matemáticas');

    // Seleccionar día LUN (toggle button)
    await page.getByText('LUN').click();

    // Verificar tipo COLEGIO está visible (por defecto)
    await expect(page.getByText('COLEGIO')).toBeVisible();

    // Guardar → mock POST devuelve subject
    await page.getByRole('button', { name: 'Guardar' }).click();

    // Verificar que la asignatura aparece en la lista
    await expect(page.getByText('Matemáticas')).toBeVisible({ timeout: 10_000 });
  });
});
