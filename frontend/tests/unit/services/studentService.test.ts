/**
 * Unit tests for studentService
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createStudent,
  getMyStudents,
  getStudent,
  updateStudent,
  deleteStudent,
} from '../../../services/studentService';
import { apiClient } from '../../../services/apiClient';

const mockAuthData = {
  token: 'mock-jwt-token',
  user: { id: '123', email: 'test@example.com', name: 'Test User' },
};

const mockStudent = {
  id: 'student-123',
  user_id: '123',
  name: 'Alex García',
  school: 'Colegio Cervantes',
  grade: '5º Primaria',
  avatar_url: 'https://example.com/avatar.png',
  allergies: ['gluten'],
  excluded_foods: ['fish'],
  created_at: '2026-01-31T10:00:00Z',
  updated_at: '2026-01-31T10:00:00Z',
};

describe('studentService', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    const localStorageMock = {
      getItem: vi.fn((key: string) => {
        if (key === 'school-agenda-auth-v2') {
          return JSON.stringify(mockAuthData);
        }
        return null;
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock as any;
  });

  describe('createStudent', () => {
    it('should create a student successfully', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockStudent as any);

      const studentData = {
        name: 'Alex García',
        school: 'Colegio Cervantes',
        grade: '5º Primaria',
        avatar_url: 'https://example.com/avatar.png',
        allergies: ['gluten'],
        excluded_foods: ['fish'],
      };

      const result = await createStudent(studentData);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/students', studentData);
      expect(result).toEqual(mockStudent);
    });

    it('should throw error when creation fails', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new Error('Validation error')
      );

      await expect(
        createStudent({
          name: '',
          school: 'Test',
          grade: 'Test',
        })
      ).rejects.toThrow('Validation error');
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      // Mock the API call to return 401 error
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new Error('Unauthorized')
      );

      await expect(
        createStudent({
          name: 'Test',
          school: 'Test',
          grade: 'Test',
        })
      ).rejects.toThrow('Unauthorized');
    });
  });

  describe('getMyStudents', () => {
    it('should fetch all students successfully', async () => {
      const students = [mockStudent, { ...mockStudent, id: 'student-456' }];

      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(students as any);

      const result = await getMyStudents();

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/students');
      expect(result).toEqual(students);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no students', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce([] as any);

      const result = await getMyStudents();

      expect(result).toEqual([]);
    });

    it('should throw error when fetch fails', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Unauthorized'));

      await expect(getMyStudents()).rejects.toThrow('Unauthorized');
    });
  });

  describe('getStudent', () => {
    it('should fetch a specific student successfully', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockStudent as any);

      const result = await getStudent('student-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/students/student-123');
      expect(result).toEqual(mockStudent);
    });

    it('should throw error when student not found', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new Error('Student not found'));

      await expect(getStudent('nonexistent')).rejects.toThrow('Student not found');
    });
  });

  describe('updateStudent', () => {
    it('should update student successfully', async () => {
      const updatedStudent = { ...mockStudent, name: 'Updated Name' };

      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updatedStudent as any);

      const result = await updateStudent('student-123', { name: 'Updated Name' });

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/students/student-123', {
        name: 'Updated Name',
      });
      expect(result.name).toBe('Updated Name');
    });

    it('should update allergies successfully', async () => {
      const updatedStudent = { ...mockStudent, allergies: ['gluten', 'lactose'] };

      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updatedStudent as any);

      const result = await updateStudent('student-123', {
        allergies: ['gluten', 'lactose'],
      });

      expect(result.allergies).toEqual(['gluten', 'lactose']);
    });

    it('should throw error when update fails', async () => {
      vi.spyOn(apiClient, 'put').mockRejectedValueOnce(new Error('Not found'));

      await expect(updateStudent('student-123', { name: 'New' })).rejects.toThrow(
        'Not found'
      );
    });

    it('should throw error when not owner', async () => {
      vi.spyOn(apiClient, 'put').mockRejectedValueOnce(
        new Error('Not authorized to update this student')
      );

      await expect(updateStudent('other-student', { name: 'Hack' })).rejects.toThrow(
        'Not authorized'
      );
    });
  });

  describe('deleteStudent', () => {
    it('should delete student successfully', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteStudent('student-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/students/student-123');
    });

    it('should throw error when delete fails', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(
        new Error('Cannot delete student')
      );

      await expect(deleteStudent('student-123')).rejects.toThrow(
        'Cannot delete student'
      );
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      // Mock the API call to return 401 error
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(
        new Error('Unauthorized')
      );

      await expect(deleteStudent('student-123')).rejects.toThrow('Unauthorized');
    });
  });
});
