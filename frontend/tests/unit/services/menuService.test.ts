import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createMenu,
  getStudentMenus,
  getMenu,
  updateMenu,
  deleteMenu,
  upsertMenu,
} from '../../../services/menuService';
import { apiClient } from '../../../services/apiClient';

const mockMenu = {
  id: 'menu-1',
  student_id: 'student-123',
  date: '2026-02-10',
  first_course: 'Sopa',
  second_course: 'Pollo asado',
  side_dish: 'Ensalada',
  dessert: 'Fruta',
  allergens: ['gluten'],
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('menuService', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    const localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock as any;
  });

  describe('createMenu', () => {
    it('should create a menu item', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockMenu as any);

      const data = {
        student_id: 'student-123',
        date: '2026-02-10',
        first_course: 'Sopa',
        second_course: 'Pollo asado',
      };
      const result = await createMenu(data);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/menus', data);
      expect(result).toEqual(mockMenu);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('Validation error'));

      await expect(
        createMenu({ student_id: '', date: '', first_course: '', second_course: '' })
      ).rejects.toThrow('Validation error');
    });
  });

  describe('getStudentMenus', () => {
    it('should fetch menus without date filters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([mockMenu] as any);

      const result = await getStudentMenus('student-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/menus/student/student-123');
      expect(result).toHaveLength(1);
    });

    it('should include start_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getStudentMenus('student-123', '2026-02-01');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/menus/student/student-123?start_date=2026-02-01'
      );
    });

    it('should include end_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getStudentMenus('student-123', undefined, '2026-02-28');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/menus/student/student-123?end_date=2026-02-28'
      );
    });

    it('should include both date parameters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getStudentMenus('student-123', '2026-02-01', '2026-02-28');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/menus/student/student-123?start_date=2026-02-01&end_date=2026-02-28'
      );
    });

    it('should return empty array when no menus', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getStudentMenus('student-123');
      expect(result).toEqual([]);
    });
  });

  describe('getMenu', () => {
    it('should fetch a specific menu', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockMenu as any);

      const result = await getMenu('menu-1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/menus/menu-1');
      expect(result).toEqual(mockMenu);
    });

    it('should propagate not found errors', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Not found'));

      await expect(getMenu('nonexistent')).rejects.toThrow('Not found');
    });
  });

  describe('updateMenu', () => {
    it('should update a menu item', async () => {
      const updated = { ...mockMenu, first_course: 'Crema de verduras' };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateMenu('menu-1', { first_course: 'Crema de verduras' });

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/menus/menu-1', {
        first_course: 'Crema de verduras',
      });
      expect(result.first_course).toBe('Crema de verduras');
    });
  });

  describe('deleteMenu', () => {
    it('should delete a menu item', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteMenu('menu-1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/menus/menu-1');
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new Error('Forbidden'));

      await expect(deleteMenu('menu-1')).rejects.toThrow('Forbidden');
    });
  });

  describe('upsertMenu', () => {
    it('should upsert a menu item', async () => {
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(mockMenu as any);

      const data = {
        student_id: 'student-123',
        date: '2026-02-10',
        first_course: 'Sopa',
        second_course: 'Pollo asado',
      };
      const result = await upsertMenu(data);

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/menus/upsert', data);
      expect(result).toEqual(mockMenu);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'put').mockRejectedValueOnce(new Error('Server error'));

      await expect(
        upsertMenu({ student_id: 'x', date: '', first_course: '', second_course: '' })
      ).rejects.toThrow('Server error');
    });
  });
});
