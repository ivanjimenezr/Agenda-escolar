import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  register,
  login,
  logout,
  getCurrentUser,
  isAuthenticated,
  getStoredUser,
} from '../../../services/authService';
import { apiClient, ApiError, saveAuthToken, removeAuthToken } from '../../../services/apiClient';

// Mock apiClient module functions
vi.mock('../../../services/apiClient', async () => {
  const actual = await vi.importActual('../../../services/apiClient');
  return {
    ...actual,
    saveAuthToken: vi.fn(),
    removeAuthToken: vi.fn(),
  };
});

const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  is_active: true,
  email_verified: true,
  created_at: '2026-01-31T10:00:00Z',
};

const mockTokenResponse = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  user: mockUser,
};

describe('authService', () => {
  let localStorageData: Record<string, string>;

  beforeEach(() => {
    vi.clearAllMocks();

    localStorageData = {};
    const localStorageMock = {
      getItem: vi.fn((key: string) => localStorageData[key] ?? null),
      setItem: vi.fn((key: string, value: string) => { localStorageData[key] = value; }),
      removeItem: vi.fn((key: string) => { delete localStorageData[key]; }),
      clear: vi.fn(),
    };
    global.localStorage = localStorageMock as any;
  });

  describe('register', () => {
    it('should register a user successfully', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockUser as any);

      const result = await register({
        email: 'test@example.com',
        password: 'Password123',
        name: 'Test User',
      });

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/auth/register', {
        email: 'test@example.com',
        password: 'Password123',
        name: 'Test User',
      });
      expect(result).toEqual(mockUser);
    });

    it('should throw "Email already registered" on 400', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new ApiError(400, 'Bad request')
      );

      await expect(
        register({ email: 'test@example.com', password: 'Password123', name: 'Test' })
      ).rejects.toThrow('Email already registered');
    });

    it('should throw "Invalid data" on 422', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new ApiError(422, 'Validation error')
      );

      await expect(
        register({ email: 'bad', password: 'x', name: '' })
      ).rejects.toThrow('Invalid data. Please check your inputs.');
    });

    it('should propagate non-ApiError errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(
        register({ email: 'test@example.com', password: 'Password123', name: 'Test' })
      ).rejects.toThrow('Network error');
    });

    it('should propagate unknown ApiError status codes', async () => {
      const apiError = new ApiError(500, 'Internal server error');
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(apiError);

      await expect(
        register({ email: 'test@example.com', password: 'Password123', name: 'Test' })
      ).rejects.toBe(apiError);
    });
  });

  describe('login', () => {
    it('should login successfully and save token', async () => {
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce(mockTokenResponse as any);

      const result = await login({ email: 'test@example.com', password: 'Password123' });

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/auth/login', {
        email: 'test@example.com',
        password: 'Password123',
      });
      expect(saveAuthToken).toHaveBeenCalledWith('mock-jwt-token');
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'school-agenda-auth-v2',
        JSON.stringify(mockUser)
      );
      expect(result).toEqual(mockUser);
    });

    it('should throw "Invalid email or password" on 401', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
        new ApiError(401, 'Unauthorized')
      );

      await expect(
        login({ email: 'test@example.com', password: 'wrong' })
      ).rejects.toThrow('Invalid email or password');
    });

    it('should propagate non-ApiError errors', async () => {
      vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('Network error'));

      await expect(
        login({ email: 'test@example.com', password: 'Password123' })
      ).rejects.toThrow('Network error');
    });
  });

  describe('logout', () => {
    it('should remove auth token and user data', () => {
      logout();
      expect(removeAuthToken).toHaveBeenCalled();
      expect(localStorage.removeItem).toHaveBeenCalledWith('school-agenda-auth-v2');
    });
  });

  describe('getCurrentUser', () => {
    it('should fetch and store current user', async () => {
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce(mockUser as any);

      const result = await getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/users/me');
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'school-agenda-auth-v2',
        JSON.stringify(mockUser)
      );
      expect(result).toEqual(mockUser);
    });

    it('should logout and throw on 401', async () => {
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(
        new ApiError(401, 'Unauthorized')
      );

      await expect(getCurrentUser()).rejects.toThrow('Session expired. Please login again.');
      expect(removeAuthToken).toHaveBeenCalled();
      expect(localStorage.removeItem).toHaveBeenCalledWith('school-agenda-auth-v2');
    });

    it('should propagate non-401 errors', async () => {
      const apiError = new ApiError(500, 'Server error');
      vi.spyOn(apiClient, 'get').mockRejectedValueOnce(apiError);

      await expect(getCurrentUser()).rejects.toBe(apiError);
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when auth-token exists', () => {
      localStorageData['auth-token'] = 'some-token';
      expect(isAuthenticated()).toBe(true);
    });

    it('should return false when no auth-token', () => {
      expect(isAuthenticated()).toBe(false);
    });
  });

  describe('getStoredUser', () => {
    it('should return parsed user from localStorage', () => {
      localStorageData['school-agenda-auth-v2'] = JSON.stringify(mockUser);
      const result = getStoredUser();
      expect(result).toEqual(mockUser);
    });

    it('should return null when no user data', () => {
      expect(getStoredUser()).toBeNull();
    });

    it('should return null for invalid JSON', () => {
      localStorageData['school-agenda-auth-v2'] = 'not-json';
      expect(getStoredUser()).toBeNull();
    });
  });
});
