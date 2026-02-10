import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createSubject,
  getSubjectsByStudent,
  getSubjectById,
  updateSubject,
  deleteSubject,
} from '../../../services/subjectService';
import { apiClient } from '../../../services/apiClient';

const mockSubject = {
  id: 'subject-1',
  student_id: 'student-123',
  name: 'Matemáticas',
  type: 'school',
  days: ['Lunes', 'Miércoles'],
  time: '09:00',
  teacher: 'Prof. García',
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('subjectService', () => {
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

  describe('createSubject', () => {
    it('should create a subject without replace flag', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockSubject as any);

      const data = { name: 'Matemáticas', type: 'school' as const, days: ['Lunes'] };
      const result = await createSubject('student-123', data);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/subjects',
        data
      );
      expect(result).toEqual(mockSubject);
    });

    it('should create a subject with replace=true', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockSubject as any);

      const data = { name: 'Matemáticas', type: 'school' as const, days: ['Lunes'] };
      await createSubject('student-123', data, true);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/subjects?replace=true',
        data
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('Validation error'));

      await expect(
        createSubject('student-123', { name: '', type: 'school' as const, days: [] })
      ).rejects.toThrow('Validation error');
    });
  });

  describe('getSubjectsByStudent', () => {
    it('should fetch all subjects for a student', async () => {
      const subjects = [mockSubject, { ...mockSubject, id: 'subject-2' }];
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(subjects as any);

      const result = await getSubjectsByStudent('student-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/students/student-123/subjects');
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no subjects', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getSubjectsByStudent('student-123');
      expect(result).toEqual([]);
    });
  });

  describe('getSubjectById', () => {
    it('should fetch a specific subject', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockSubject as any);

      const result = await getSubjectById('student-123', 'subject-1');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/subjects/subject-1'
      );
      expect(result).toEqual(mockSubject);
    });

    it('should propagate not found errors', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Not found'));

      await expect(getSubjectById('student-123', 'nonexistent')).rejects.toThrow('Not found');
    });
  });

  describe('updateSubject', () => {
    it('should update a subject', async () => {
      const updated = { ...mockSubject, name: 'Lengua' };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateSubject('student-123', 'subject-1', { name: 'Lengua' });

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/students/student-123/subjects/subject-1',
        { name: 'Lengua' }
      );
      expect(result.name).toBe('Lengua');
    });
  });

  describe('deleteSubject', () => {
    it('should delete a subject', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteSubject('student-123', 'subject-1');

      expect(apiClient.delete).toHaveBeenCalledWith(
        '/api/v1/students/student-123/subjects/subject-1'
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new Error('Forbidden'));

      await expect(deleteSubject('student-123', 'subject-1')).rejects.toThrow('Forbidden');
    });
  });
});
