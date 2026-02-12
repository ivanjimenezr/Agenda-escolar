/**
 * API Client Configuration
 * Base client for making HTTP requests to the backend API
 */

// API Base URL - uses environment variable with fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://agenda-escolar-pnpk.onrender.com';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.message = message;

    // Ensure error is properly serialized
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  toString(): string {
    return `${this.name} (${this.status}): ${this.message}`;
  }

  toJSON() {
    return {
      name: this.name,
      status: this.status,
      message: this.message,
      details: this.details
    };
  }
}

/**
 * Get authentication token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth-token');
};

/**
 * Save authentication token to localStorage
 */
export const saveAuthToken = (token: string): void => {
  localStorage.setItem('auth-token', token);
};

/**
 * Remove authentication token from localStorage
 */
export const removeAuthToken = (): void => {
  localStorage.removeItem('auth-token');
};

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Default headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authentication token if available
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    console.debug(`[API] ${options.method || 'GET'} ${url}`);

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`[API Error] ${response.status}:`, errorData);

      // Handle 401 Unauthorized - session expired or invalid token
      if (response.status === 401) {
        console.warn('[API] 401 Unauthorized - Clearing session');
        removeAuthToken();
        // Clear user from localStorage to trigger logout
        localStorage.removeItem('school-agenda-auth-v2');
        // Dispatch event so React can update auth state without a page reload.
        // window.location.reload() must NOT be used here: if something keeps
        // returning 401 on page load the reload would create an infinite loop.
        window.dispatchEvent(new CustomEvent('auth:session-expired'));
      }

      throw new ApiError(
        response.status,
        errorData.detail || errorData.message || 'Request failed',
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network error or other fetch errors
    throw new ApiError(
      0,
      error instanceof Error ? error.message : 'Network error',
      error
    );
  }
}

/**
 * HTTP Methods
 */
export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit): Promise<T> => {
    return apiFetch<T>(endpoint, { ...options, method: 'GET' });
  },

  post: <T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  put: <T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  patch: <T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  delete: <T>(endpoint: string, options?: RequestInit): Promise<T> => {
    return apiFetch<T>(endpoint, { ...options, method: 'DELETE' });
  },
};
