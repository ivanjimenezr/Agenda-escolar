/**
 * User Service
 *
 * API client for user-related operations
 */

import { apiClient, removeAuthToken, ApiError } from './apiClient';

interface UserUpdateData {
  name?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
}

interface ApiUser {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

function ensureAuthToken(): void {
  const token = localStorage.getItem('auth-token');
  if (!token) {
    throw new Error('No authentication token found');
  }
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<ApiUser> {
  ensureAuthToken();
  try {
    const user = await apiClient.get<ApiUser>('/api/v1/users/me');
    localStorage.setItem('school-agenda-auth-v2', JSON.stringify(user));
    return user;
  } catch (error: any) {
    if (error instanceof ApiError && error.status === 401) {
      // Clear tokens on auth error
      removeAuthToken();
      localStorage.removeItem('school-agenda-auth-v2');
      throw new Error('Session expired. Please login again.');
    }
    throw error;
  }
}

/**
 * Update current user information
 */
export async function updateCurrentUser(data: UserUpdateData): Promise<ApiUser> {
  ensureAuthToken();
  try {
    const user = await apiClient.put<ApiUser>('/api/v1/users/me', data);
    localStorage.setItem('school-agenda-auth-v2', JSON.stringify(user));
    return user;
  } catch (error: any) {
    if (error instanceof ApiError && error.status === 401) {
      removeAuthToken();
      localStorage.removeItem('school-agenda-auth-v2');
      throw new Error('Session expired. Please login again.');
    }
    throw error;
  }
}

/**
 * Delete current user account
 */
export async function deleteCurrentUser(): Promise<void> {
  ensureAuthToken();
  try {
    await apiClient.delete<void>('/api/v1/users/me');
    removeAuthToken();
    localStorage.removeItem('school-agenda-auth-v2');
  } catch (error: any) {
    if (error instanceof ApiError && error.status === 401) {
      removeAuthToken();
      localStorage.removeItem('school-agenda-auth-v2');
      throw new Error('Session expired. Please login again.');
    }
    throw error;
  }
}
