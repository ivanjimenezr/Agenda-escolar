/**
 * Dinner Service
 *
 * API client for dinner operations and AI-powered suggestions
 */

import { apiClient } from './apiClient';

export interface Dinner {
  id: string;
  student_id: string;
  date: string;
  meal: string;
  ingredients: string[];
  created_at: string;
  updated_at: string;
}

export interface GenerateDinnerRequest {
  type: 'today' | 'week';
  target_date?: string; // YYYY-MM-DD format
}

export interface CreateDinnerRequest {
  date: string;
  meal: string;
  ingredients?: string[];
}

export interface UpdateDinnerRequest {
  meal?: string;
  ingredients?: string[];
}

export interface ShoppingListRequest {
  scope: 'today' | 'week' | 'custom';
  start_date?: string;
  end_date?: string;
  num_people?: number;
}

export interface ShoppingListCategory {
  category: string;
  items: string[];
}

export interface ShoppingListResponse {
  categories: ShoppingListCategory[];
}

/**
 * Generate dinner suggestions using AI
 */
export const generateDinners = async (
  studentId: string,
  request: GenerateDinnerRequest
): Promise<Dinner[]> => {
  return apiClient.post<Dinner[]>(
    `/api/v1/students/${studentId}/dinners/generate`,
    request
  );
};

/**
 * Create a dinner manually
 */
export const createDinner = async (
  studentId: string,
  data: CreateDinnerRequest
): Promise<Dinner> => {
  return apiClient.post<Dinner>(`/api/v1/students/${studentId}/dinners`, data);
};

/**
 * Get all dinners for a student
 */
export const getDinners = async (
  studentId: string,
  startDate?: string,
  endDate?: string
): Promise<Dinner[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const query = params.toString();
  const url = `/api/v1/students/${studentId}/dinners${query ? `?${query}` : ''}`;

  return apiClient.get<Dinner[]>(url);
};

/**
 * Update a dinner
 */
export const updateDinner = async (
  studentId: string,
  dinnerId: string,
  data: UpdateDinnerRequest
): Promise<Dinner> => {
  return apiClient.put<Dinner>(
    `/api/v1/students/${studentId}/dinners/${dinnerId}`,
    data
  );
};

/**
 * Delete a dinner
 */
export const deleteDinner = async (
  studentId: string,
  dinnerId: string
): Promise<void> => {
  return apiClient.delete<void>(
    `/api/v1/students/${studentId}/dinners/${dinnerId}`
  );
};

/**
 * Generate shopping list from dinners
 */
export const generateShoppingList = async (
  studentId: string,
  request: ShoppingListRequest
): Promise<ShoppingListResponse> => {
  return apiClient.post<ShoppingListResponse>(
    `/api/v1/students/${studentId}/dinners/shopping-list`,
    request
  );
};
