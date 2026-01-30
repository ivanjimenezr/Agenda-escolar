/**
 * Menu Service
 *
 * API client for school menu operations
 */

import { apiClient } from './apiClient';

export interface MenuItem {
  id: string;
  student_id: string;
  date: string; // ISO date string
  first_course: string;
  second_course: string;
  side_dish: string | null;
  dessert: string | null;
  allergens: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateMenuRequest {
  student_id: string;
  date: string; // ISO date string (YYYY-MM-DD)
  first_course: string;
  second_course: string;
  side_dish?: string;
  dessert?: string;
  allergens?: string[];
}

export interface UpdateMenuRequest {
  date?: string;
  first_course?: string;
  second_course?: string;
  side_dish?: string;
  dessert?: string;
  allergens?: string[];
}

/**
 * Create a new menu item
 */
export const createMenu = async (data: CreateMenuRequest): Promise<MenuItem> => {
  return apiClient.post<MenuItem>('/api/v1/menus', data);
};

/**
 * Get all menu items for a student
 */
export const getStudentMenus = async (
  studentId: string,
  startDate?: string,
  endDate?: string
): Promise<MenuItem[]> => {
  let url = `/api/v1/menus/student/${studentId}`;
  const params = new URLSearchParams();

  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  return apiClient.get<MenuItem[]>(url);
};

/**
 * Get a specific menu item by ID
 */
export const getMenu = async (menuId: string): Promise<MenuItem> => {
  return apiClient.get<MenuItem>(`/api/v1/menus/${menuId}`);
};

/**
 * Update a menu item
 */
export const updateMenu = async (
  menuId: string,
  data: UpdateMenuRequest
): Promise<MenuItem> => {
  return apiClient.put<MenuItem>(`/api/v1/menus/${menuId}`, data);
};

/**
 * Delete a menu item
 */
export const deleteMenu = async (menuId: string): Promise<void> => {
  return apiClient.delete<void>(`/api/v1/menus/${menuId}`);
};
