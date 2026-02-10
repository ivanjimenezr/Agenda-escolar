import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createExam,
  getExamsByStudent,
  getExamById,
  updateExam,
  deleteExam,
} from '../../../services/examService';
import { apiClient } from '../../../services/apiClient';

const mockExam = {
  id: 'exam-1',
  student_id: 'student-123',
  subject: 'Matemáticas',
  date: '2026-03-15',
  topic: 'Ecuaciones',
  notes: 'Tema 5',
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('examService', () => {
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

  describe('createExam', () => {
    it('should create an exam', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockExam as any);

      const data = { subject: 'Matemáticas', date: '2026-03-15', topic: 'Ecuaciones' };
      const result = await createExam('student-123', data);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams',
        data
      );
      expect(result).toEqual(mockExam);
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('Validation error'));

      await expect(
        createExam('student-123', { subject: '', date: '', topic: '' })
      ).rejects.toThrow('Validation error');
    });
  });

  describe('getExamsByStudent', () => {
    it('should fetch exams without date filters', async () => {
      const exams = [mockExam];
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(exams as any);

      const result = await getExamsByStudent('student-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/students/student-123/exams');
      expect(result).toEqual(exams);
    });

    it('should include from_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getExamsByStudent('student-123', '2026-03-01');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams?from_date=2026-03-01'
      );
    });

    it('should include to_date parameter', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getExamsByStudent('student-123', undefined, '2026-03-31');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams?to_date=2026-03-31'
      );
    });

    it('should include both date parameters', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      await getExamsByStudent('student-123', '2026-03-01', '2026-03-31');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams?from_date=2026-03-01&to_date=2026-03-31'
      );
    });

    it('should return empty array when no exams', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getExamsByStudent('student-123');
      expect(result).toEqual([]);
    });
  });

  describe('getExamById', () => {
    it('should fetch a specific exam', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockExam as any);

      const result = await getExamById('student-123', 'exam-1');

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams/exam-1'
      );
      expect(result).toEqual(mockExam);
    });
  });

  describe('updateExam', () => {
    it('should update an exam', async () => {
      const updated = { ...mockExam, topic: 'Fracciones' };
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updated as any);

      const result = await updateExam('student-123', 'exam-1', { topic: 'Fracciones' });

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams/exam-1',
        { topic: 'Fracciones' }
      );
      expect(result.topic).toBe('Fracciones');
    });
  });

  describe('deleteExam', () => {
    it('should delete an exam', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteExam('student-123', 'exam-1');

      expect(apiClient.delete).toHaveBeenCalledWith(
        '/api/v1/students/student-123/exams/exam-1'
      );
    });

    it('should propagate errors', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new Error('Not found'));

      await expect(deleteExam('student-123', 'exam-1')).rejects.toThrow('Not found');
    });
  });
});
