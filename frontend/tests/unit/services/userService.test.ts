/**
 * Unit tests for userService
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getCurrentUser, updateCurrentUser, deleteCurrentUser } from '../../../services/userService';

// Mock fetch globally
global.fetch = vi.fn();

const mockAuthData = {
  token: 'mock-jwt-token',
  user: {
    id: '123',
    email: 'test@example.com',
    name: 'Test User',
  },
};

const mockUser = {
  id: '123',
  email: 'test@example.com',
  name: 'Test User',
  is_active: true,
  email_verified: false,
  created_at: '2026-01-31T10:00:00Z',
};

describe('userService', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();

    // Mock localStorage
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

  describe('getCurrentUser', () => {
    it('should fetch current user successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/users/me',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
        }
      );
      expect(result).toEqual(mockUser);
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(getCurrentUser()).rejects.toThrow('No authentication token found');
    });

    it('should throw error when request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateCurrentUser', () => {
    it('should update user name successfully', async () => {
      const updatedUser = { ...mockUser, name: 'Updated Name' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedUser,
      });

      const result = await updateCurrentUser({ name: 'Updated Name' });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/users/me',
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
          body: JSON.stringify({ name: 'Updated Name' }),
        }
      );
      expect(result).toEqual(updatedUser);
    });

    it('should update user email successfully', async () => {
      const updatedUser = { ...mockUser, email: 'newemail@example.com' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedUser,
      });

      const result = await updateCurrentUser({ email: 'newemail@example.com' });

      expect(result.email).toBe('newemail@example.com');
    });

    it('should update password successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await updateCurrentUser({
        current_password: 'OldPass123',
        new_password: 'NewPass456',
      });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/users/me',
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-jwt-token',
          },
          body: JSON.stringify({
            current_password: 'OldPass123',
            new_password: 'NewPass456',
          }),
        }
      );
      expect(result).toEqual(mockUser);
    });

    it('should throw error when update fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already registered' }),
      });

      await expect(
        updateCurrentUser({ email: 'taken@example.com' })
      ).rejects.toThrow('Email already registered');
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(updateCurrentUser({ name: 'New Name' })).rejects.toThrow(
        'No authentication token found'
      );
    });
  });

  describe('deleteCurrentUser', () => {
    it('should delete user account successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
      });

      await deleteCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        'https://agenda-escolar-pnpk.onrender.com/api/v1/users/me',
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
        json: async () => ({ detail: 'Cannot delete user' }),
      });

      await expect(deleteCurrentUser()).rejects.toThrow('Cannot delete user');
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(deleteCurrentUser()).rejects.toThrow('No authentication token found');
    });
  });
});
