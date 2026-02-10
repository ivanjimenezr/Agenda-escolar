import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  generateDinners,
  createDinner,
  getDinners,
  updateDinner,
  deleteDinner,
  generateShoppingList,
} from '../../../services/dinnerService';
import { apiClient } from '../../../services/apiClient';

const mockDinner = {
  id: 'dinner-1',
  student_id: 'student-123',
  date: '2026-02-10',
  meal: 'Tortilla de patatas',
  ingredients: ['huevos', 'patatas', 'aceite'],
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('dinnerService', () => {
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

  describe('generateDinners', () => {
    it('should generate dinners for today', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce([mockDinner] as any);

      const result = await generateDinners('student-123', { type: 'today' });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/generate',
        { type: 'today' }
      );
      expect(result).toHaveLength(1);
    });

    it('should generate dinners for a week', async () => {
      const weekDinners = Array.from({ length: 7 }, (_, i) => ({
        ...mockDinner,
        id: `dinner-${i}`,
      }));
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(weekDinners as any);

      const result = await generateDinners('student-123', { type: 'week' });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/generate',
        { type: 'week' }
      );
      expect(result).toHaveLength(7);
    });

    it('should include target_date when provided', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce([mockDinner] as any);

      await generateDinners('student-123', { type: 'today', target_date: '2026-02-15' });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/generate',
        { type: 'today', target_date: '2026-02-15' }
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('AI generation failed'));

      await expect(
        generateDinners('student-123', { type: 'today' })
      ).rejects.toThrow('AI generation failed');
    });
  });

  describe('createDinner', () => {
    it('should create a dinner manually', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockDinner as any);

      const data = { date: '2026-02-10', meal: 'Tortilla de patatas', ingredients: ['huevos'] };
      const result = await createDinner('student-123', data);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners',
        data
      );
      expect(result).toEqual(mockDinner);
    });
  });

  describe('getDinners', () => {
    it('should fetch dinners without date filters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([mockDinner] as any);

      const result = await getDinners('student-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/students/student-123/dinners');
      expect(result).toHaveLength(1);
    });

    it('should include start_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getDinners('student-123', '2026-02-01');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners?start_date=2026-02-01'
      );
    });

    it('should include end_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getDinners('student-123', undefined, '2026-02-28');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners?end_date=2026-02-28'
      );
    });

    it('should include both date parameters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getDinners('student-123', '2026-02-01', '2026-02-28');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners?start_date=2026-02-01&end_date=2026-02-28'
      );
    });

    it('should return empty array when no dinners', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getDinners('student-123');
      expect(result).toEqual([]);
    });
  });

  describe('updateDinner', () => {
    it('should update a dinner', async () => {
      const updated = { ...mockDinner, meal: 'Ensalada César' };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateDinner('student-123', 'dinner-1', { meal: 'Ensalada César' });

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/dinner-1',
        { meal: 'Ensalada César' }
      );
      expect(result.meal).toBe('Ensalada César');
    });
  });

  describe('deleteDinner', () => {
    it('should delete a dinner', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteDinner('student-123', 'dinner-1');

      expect(apiClient.delete).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/dinner-1'
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new Error('Not found'));

      await expect(deleteDinner('student-123', 'dinner-1')).rejects.toThrow('Not found');
    });
  });

  describe('generateShoppingList', () => {
    it('should generate shopping list for today', async () => {
      const mockResponse = {
        categories: [
          { category: 'Verduras', items: ['Patatas', 'Cebollas'] },
          { category: 'Proteínas', items: ['Huevos'] },
        ],
      };
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockResponse as any);

      const result = await generateShoppingList('student-123', { scope: 'today' });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/shopping-list',
        { scope: 'today' }
      );
      expect(result.categories).toHaveLength(2);
    });

    it('should generate shopping list with custom dates', async () => {
      const mockResponse = { categories: [] };
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockResponse as any);

      await generateShoppingList('student-123', {
        scope: 'custom',
        start_date: '2026-02-01',
        end_date: '2026-02-07',
        num_people: 4,
      });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/dinners/shopping-list',
        { scope: 'custom', start_date: '2026-02-01', end_date: '2026-02-07', num_people: 4 }
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('AI error'));

      await expect(
        generateShoppingList('student-123', { scope: 'week' })
      ).rejects.toThrow('AI error');
    });
  });
});
