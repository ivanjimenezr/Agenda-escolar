import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getActiveModules,
  updateActiveModules,
} from '../../../services/activeModulesService';
import { apiClient } from '../../../services/apiClient';

const mockModules = {
  id: 'modules-1',
  student_id: 'student-123',
  subjects: true,
  exams: true,
  menu: true,
  events: true,
  dinner: true,
  contacts: true,
};

describe('activeModulesService', () => {
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

  describe('getActiveModules', () => {
    it('should fetch active modules for a student', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockModules as any);

      const result = await getActiveModules('student-123');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/active-modules'
      );
      expect(result).toEqual(mockModules);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Not found'));

      await expect(getActiveModules('student-123')).rejects.toThrow('Not found');
    });
  });

  describe('updateActiveModules', () => {
    it('should update active modules', async () => {
      const updated = { ...mockModules, dinner: false, contacts: false };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateActiveModules('student-123', {
        dinner: false,
        contacts: false,
      });

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/students/student-123/active-modules',
        { dinner: false, contacts: false }
      );
      expect(result.dinner).toBe(false);
      expect(result.contacts).toBe(false);
    });

    it('should update a single module', async () => {
      const updated = { ...mockModules, exams: false };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateActiveModules('student-123', { exams: false });

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/students/student-123/active-modules',
        { exams: false }
      );
      expect(result.exams).toBe(false);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'put').mockRejectedValueOnce(new Error('Forbidden'));

      await expect(
        updateActiveModules('student-123', { subjects: false })
      ).rejects.toThrow('Forbidden');
    });
  });
});
