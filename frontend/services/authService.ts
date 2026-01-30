/**
 * Authentication Service
 * Handles user registration, login, and authentication state
 */

import { apiClient, saveAuthToken, removeAuthToken, ApiError } from './apiClient';

// Types matching backend schemas
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Register a new user
 */
export const register = async (data: RegisterRequest): Promise<User> => {
  try {
    const user = await apiClient.post<User>('/api/v1/auth/register', data);
    return user;
  } catch (error) {
    if (error instanceof ApiError) {
      // Handle specific error cases
      if (error.status === 400) {
        throw new Error('Email already registered');
      }
      if (error.status === 422) {
        throw new Error('Invalid data. Please check your inputs.');
      }
    }
    throw error;
  }
};

/**
 * Login user and save token
 */
export const login = async (data: LoginRequest): Promise<User> => {
  try {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', data);

    // Save token to localStorage
    saveAuthToken(response.access_token);

    // Save user data to localStorage
    localStorage.setItem('school-agenda-auth-v2', JSON.stringify(response.user));

    return response.user;
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 401) {
        throw new Error('Invalid email or password');
      }
    }
    throw error;
  }
};

/**
 * Logout user (clear token and user data)
 */
export const logout = (): void => {
  removeAuthToken();
  localStorage.removeItem('school-agenda-auth-v2');
};

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const user = await apiClient.get<User>('/api/v1/users/me');

    // Update localStorage with fresh user data
    localStorage.setItem('school-agenda-auth-v2', JSON.stringify(user));

    return user;
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 401) {
        // Token expired or invalid - logout
        logout();
        throw new Error('Session expired. Please login again.');
      }
    }
    throw error;
  }
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('auth-token');
  return !!token;
};

/**
 * Get user from localStorage (without API call)
 */
export const getStoredUser = (): User | null => {
  const userData = localStorage.getItem('school-agenda-auth-v2');
  if (!userData) return null;

  try {
    return JSON.parse(userData);
  } catch {
    return null;
  }
};
