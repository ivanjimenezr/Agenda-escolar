import { test, expect } from '@playwright/test';
import { setupMockApi } from './helpers/mock-api';

test.describe('Autenticación', () => {
  test('registro completo e inicio de sesión automático', async ({ page }) => {
    await setupMockApi(page);
    await page.goto('/');

    // Pantalla de login visible
    await expect(page.getByText('Bienvenido de nuevo')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Iniciar Sesión' })).toBeVisible();

    // Cambiar a modo registro
    await page.getByText('Crea una cuenta ahora').click();
    await expect(page.getByText('Crea tu cuenta')).toBeVisible();

    // Rellenar formulario de registro
    await page.getByPlaceholder('Ej: Juan Pérez').fill('Test User');
    await page.getByPlaceholder('tu@email.com').fill('test@e2e.com');
    await page.getByPlaceholder('••••••••').fill('TestPass1');

    // Click registrarme
    await page.getByRole('button', { name: 'Registrarme' }).click();

    // Tras registro + auto-login, el usuario llega a la app
    // (ve el botón de crear perfil o la home, ya no ve el login)
    await expect(page.getByText('Bienvenido de nuevo')).not.toBeVisible({ timeout: 10_000 });
  });

  test('inicio de sesión con credenciales válidas', async ({ page }) => {
    await setupMockApi(page);
    await page.goto('/');

    // Rellenar formulario de login
    await page.getByPlaceholder('tu@email.com').fill('test@e2e.com');
    await page.getByPlaceholder('••••••••').fill('TestPass1');

    // Click iniciar sesión
    await page.getByRole('button', { name: 'Iniciar Sesión' }).click();

    // Llega a la app (desaparece la pantalla de login)
    await expect(page.getByText('Bienvenido de nuevo')).not.toBeVisible({ timeout: 10_000 });
  });
});
