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

// Mock fetch globally
global.fetch = vi.fn();

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
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStudent,
      });

      const studentData = {
        name: 'Alex García',
        school: 'Colegio Cervantes',
        grade: '5º Primaria',
        avatar_url: 'https://example.com/avatar.png',
        allergies: ['gluten'],
        excluded_foods: ['fish'],
      };

      const result = await createStudent(studentData);

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/students',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
          body: JSON.stringify(studentData),
        }
      );
      expect(result).toEqual(mockStudent);
    });

    it('should throw error when creation fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Validation error' }),
      });

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

      await expect(
        createStudent({
          name: 'Test',
          school: 'Test',
          grade: 'Test',
        })
      ).rejects.toThrow('No authentication token found');
    });
  });

  describe('getMyStudents', () => {
    it('should fetch all students successfully', async () => {
      const students = [mockStudent, { ...mockStudent, id: 'student-456' }];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => students,
      });

      const result = await getMyStudents();

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/students',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
        }
      );
      expect(result).toEqual(students);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no students', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      const result = await getMyStudents();

      expect(result).toEqual([]);
    });

    it('should throw error when fetch fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(getMyStudents()).rejects.toThrow('Unauthorized');
    });
  });

  describe('getStudent', () => {
    it('should fetch a specific student successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStudent,
      });

      const result = await getStudent('student-123');

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/students/student-123',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
        }
      );
      expect(result).toEqual(mockStudent);
    });

    it('should throw error when student not found', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Student not found' }),
      });

      await expect(getStudent('nonexistent')).rejects.toThrow('Student not found');
    });
  });

  describe('updateStudent', () => {
    it('should update student successfully', async () => {
      const updatedStudent = { ...mockStudent, name: 'Updated Name' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedStudent,
      });

      const result = await updateStudent('student-123', { name: 'Updated Name' });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/students/student-123',
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
          body: JSON.stringify({ name: 'Updated Name' }),
        }
      );
      expect(result.name).toBe('Updated Name');
    });

    it('should update allergies successfully', async () => {
      const updatedStudent = { ...mockStudent, allergies: ['gluten', 'lactose'] };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedStudent,
      });

      const result = await updateStudent('student-123', {
        allergies: ['gluten', 'lactose'],
      });

      expect(result.allergies).toEqual(['gluten', 'lactose']);
    });

    it('should throw error when update fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Not found' }),
      });

      await expect(updateStudent('student-123', { name: 'New' })).rejects.toThrow(
        'Not found'
      );
    });

    it('should throw error when not owner', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Not authorized to update this student' }),
      });

      await expect(updateStudent('other-student', { name: 'Hack' })).rejects.toThrow(
        'Not authorized'
      );
    });
  });

  describe('deleteStudent', () => {
    it('should delete student successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
      });

      await deleteStudent('student-123');

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/students/student-123',
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
        }
      );
    });

    it('should throw error when delete fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Cannot delete student' }),
      });

      await expect(deleteStudent('student-123')).rejects.toThrow(
        'Cannot delete student'
      );
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(deleteStudent('student-123')).rejects.toThrow(
        'No authentication token found'
      );
    });
  });
});
