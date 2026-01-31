/**
 * Unit tests for userService
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getCurrentUser, updateCurrentUser, deleteCurrentUser } from '../../../services/userService';

import { apiClient, ApiError } from '../../../services/apiClient';

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
          return JSON.stringify(mockAuthData.user);
        }
        if (key === 'auth-token') {
          return mockAuthData.token;
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
        vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockUser as any);

      const result = await getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/users/me');
      expect(result).toEqual(mockUser);
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(getCurrentUser()).rejects.toThrow('No authentication token found');
    });

    it('should throw error when request fails', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(new ApiError(401, 'Unauthorized', { detail: 'Unauthorized' }));

      await expect(getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateCurrentUser', () => {
    it('should update user name successfully', async () => {
      const updatedUser = { ...mockUser, name: 'Updated Name' };

      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updatedUser as any);

      const result = await updateCurrentUser({ name: 'Updated Name' });

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/users/me', { name: 'Updated Name' });
      expect(result).toEqual(updatedUser);
    });

    it('should update user email successfully', async () => {
      const updatedUser = { ...mockUser, email: 'newemail@example.com' };

      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(updatedUser as any);

      const result = await updateCurrentUser({ email: 'newemail@example.com' });

      expect(result.email).toBe('newemail@example.com');
    });

    it('should update password successfully', async () => {
      vi.spyOn(apiClient, 'put').mockResolvedValueOnce(mockUser as any);

      const result = await updateCurrentUser({
        current_password: 'OldPass123',
        new_password: 'NewPass456',
      });

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/users/me', {
        current_password: 'OldPass123',
        new_password: 'NewPass456',
      });
      expect(result).toEqual(mockUser);
    });

    it('should throw error when update fails', async () => {
      vi.spyOn(apiClient, 'put').mockRejectedValueOnce(new ApiError(400, 'Email already registered', { detail: 'Email already registered' }));

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
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({} as any);

      await deleteCurrentUser();

      expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/users/me');
      expect(localStorage.removeItem).toHaveBeenCalledWith('school-agenda-auth-v2');
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth-token');
    });

    it('should throw error when delete fails', async () => {
      vi.spyOn(apiClient, 'delete').mockRejectedValueOnce(new ApiError(400, 'Cannot delete user', { detail: 'Cannot delete user' }));

      await expect(deleteCurrentUser()).rejects.toThrow('Cannot delete user');
    });

    it('should throw error when not authenticated', async () => {
      localStorage.getItem = vi.fn(() => null);

      await expect(deleteCurrentUser()).rejects.toThrow('No authentication token found');
    });
  });
});
