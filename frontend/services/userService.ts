/**
 * User Service
 *
 * API client for user-related operations
 */

const API_BASE_URL = 'https://agenda-escolar-pnpk.onrender.com/api/v1';

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

/**
 * Get authorization header with JWT token
 */
function getAuthHeader(): { Authorization: string } {
  const authData = localStorage.getItem('school-agenda-auth-v2');
  if (!authData) {
    throw new Error('No authentication token found');
  }

  const { token } = JSON.parse(authData);
  return { Authorization: `Bearer ${token}` };
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<ApiUser> {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get user' }));
    throw new Error(error.detail || 'Failed to get user');
  }

  return response.json();
}

/**
 * Update current user information
 */
export async function updateCurrentUser(data: UserUpdateData): Promise<ApiUser> {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update user' }));
    throw new Error(error.detail || 'Failed to update user');
  }

  return response.json();
}

/**
 * Delete current user account
 */
export async function deleteCurrentUser(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete user' }));
    throw new Error(error.detail || 'Failed to delete user');
  }
}
